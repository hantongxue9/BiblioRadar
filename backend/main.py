"""
图情雷达（BiblioRadar）后端主入口

调度抓取和评估逻辑，将最终结果写入前端的 public/data.json。
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# Windows 控制台 UTF-8 输出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv

# 加载项目根目录的 .env 文件
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from scraper import (
    fetch_all_async,
    fetch_mock_papers,
    fetch_mock_news,
)
from llm_evaluator import evaluate_papers, evaluate_news, generate_daily_report
from data_contract import validate_items
from pipeline_utils import build_report_stats, compute_composite_score, merge_items


# ============================================================
# 配置
# ============================================================

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "public" / "data.json"
DAILY_REPORTS_PATH = OUTPUT_PATH.parent / "daily_reports.json"

USE_MOCK = os.environ.get("USE_MOCK", "false").lower() == "true"
FILTER_AFFILIATION = os.environ.get("FILTER_AFFILIATION", "false").lower() == "true"
MIN_SCORE_AVG = float(os.environ.get("MIN_SCORE_AVG", "6.0"))
LLM_MODEL = os.environ.get("LLM_MODEL", "mimo-v2.5-pro")
APP_TIMEZONE = os.environ.get("APP_TIMEZONE", "Asia/Shanghai")

# 加权综合分权重
WEIGHT_FRONTIER = float(os.environ.get("WEIGHT_FRONTIER", "0.40"))
WEIGHT_PRACTICAL = float(os.environ.get("WEIGHT_PRACTICAL", "0.35"))
WEIGHT_RIGOR = float(os.environ.get("WEIGHT_RIGOR", "0.25"))

# 精选阈值
FEATURED_THRESHOLD = float(os.environ.get("FEATURED_THRESHOLD", "7.5"))

# data.json 最大条目数（超出裁剪最旧的）
MAX_TOTAL_ITEMS = int(os.environ.get("MAX_TOTAL_ITEMS", "500"))

# 出版商 API Key（可选，未配置时 fallback 到 RSS）
os.environ.setdefault("ELSEVIER_API_KEY", os.environ.get("ELSEVIER_API_KEY", ""))
os.environ.setdefault("SPRINGER_API_KEY", os.environ.get("SPRINGER_API_KEY", ""))


def now_local() -> datetime:
    """Return current time in the app's reporting timezone."""
    return datetime.now(ZoneInfo(APP_TIMEZONE))


# ============================================================
# 主流程
# ============================================================

def load_existing_data() -> list:
    """加载已有的 data.json"""
    if OUTPUT_PATH.exists():
        try:
            with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def load_daily_reports() -> list:
    """加载已有的 daily_reports.json"""
    if DAILY_REPORTS_PATH.exists():
        try:
            with open(DAILY_REPORTS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_daily_reports(reports: list):
    """写入 daily_reports.json"""
    DAILY_REPORTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DAILY_REPORTS_PATH, "w", encoding="utf-8") as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)


def main():
    """主流程：抓取论文 + 资讯 → 评估 → 综合分 → 写入"""
    run_started_at = now_local()
    print(f"[main] BiblioRadar 数据更新开始 {run_started_at.isoformat()}")
    print(f"[main] 输出路径: {OUTPUT_PATH}")

    # 加载已有数据，用于去重
    existing = load_existing_data()
    existing_titles = {p["title"].lower().strip() for p in existing}

    # 第一步：抓取（一次异步调用获取所有源）
    if USE_MOCK:
        print("[main] 使用 mock 数据")
        raw_papers = fetch_mock_papers()
        raw_news = fetch_mock_news()
    else:
        print("[main] 从信源池异步抓取")
        raw_papers, raw_news = asyncio.run(
            fetch_all_async(apply_affiliation_filter=FILTER_AFFILIATION)
        )

    # 过滤已存在的条目
    new_papers = [p for p in raw_papers if p["title"].lower().strip() not in existing_titles]
    new_news = [n for n in raw_news if n["title"].lower().strip() not in existing_titles]
    print(f"[main] 新论文 {len(new_papers)} 篇，新资讯 {len(new_news)} 条")

    evaluated = []

    # 第二步：评估论文
    if new_papers:
        print(f"[main] 开始评估 {len(new_papers)} 篇论文")
        eval_papers = evaluate_papers(
            new_papers,
            model=LLM_MODEL,
            min_score_avg=MIN_SCORE_AVG,
        )
        evaluated.extend(eval_papers)
        print(f"[main] 论文通过 {len(eval_papers)} 篇")

    # 第三步：评估资讯
    if new_news:
        print(f"[main] 开始评估 {len(new_news)} 条资讯")
        eval_news = evaluate_news(
            new_news,
            model=LLM_MODEL,
            min_score_avg=5.0,
        )
        evaluated.extend(eval_news)
        print(f"[main] 资讯通过 {len(eval_news)} 条")

    # 第四步：计算综合分并合并写入
    if evaluated:
        for item in evaluated:
            compute_composite_score(
                item,
                featured_threshold=FEATURED_THRESHOLD,
                weight_frontier=WEIGHT_FRONTIER,
                weight_practical=WEIGHT_PRACTICAL,
                weight_rigor=WEIGHT_RIGOR,
            )

        merged = merge_items(existing, evaluated)

        if len(merged) > MAX_TOTAL_ITEMS:
            merged = merged[:MAX_TOTAL_ITEMS]
            print(f"[main] 裁剪至 {MAX_TOTAL_ITEMS} 条")

        validation_errors = validate_items(merged)
        if validation_errors:
            raise ValueError(
                "data.json 契约校验失败:\n" + "\n".join(validation_errors)
            )

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = OUTPUT_PATH.with_suffix(".json.tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)
        tmp_path.replace(OUTPUT_PATH)
        print(f"[main] 已写入 {len(merged)} 条到 {OUTPUT_PATH}")
    else:
        print(f"[main] 无新条目需要写入")

    # 第五步：生成日报（基于当天抓取的全部内容，不仅是新增的）
    today_str = run_started_at.strftime("%Y-%m-%d")
    report_items = evaluated if evaluated else raw_papers + raw_news
    print(f"[main] 生成 {today_str} 日报（基于 {len(report_items)} 条）...")
    report = generate_daily_report(report_items, model=LLM_MODEL)
    if report:
        reports = load_daily_reports()
        reports = [r for r in reports if r.get("date") != today_str]
        reports.append({
            "date": today_str,
            "summary": report["summary"],
            "highlights": report["highlights"],
            "stats": build_report_stats(report_items),
        })
        reports.sort(key=lambda r: r["date"], reverse=True)
        save_daily_reports(reports)
        print(f"[main] 日报已写入 {DAILY_REPORTS_PATH}")
    else:
        print(f"[main] 日报生成失败，跳过")

    print(f"[main] 数据更新完成")


if __name__ == "__main__":
    main()
