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


# ============================================================
# 配置
# ============================================================

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "public" / "data.json"
DAILY_REPORTS_PATH = OUTPUT_PATH.parent / "daily_reports.json"

USE_MOCK = os.environ.get("USE_MOCK", "false").lower() == "true"
FILTER_AFFILIATION = os.environ.get("FILTER_AFFILIATION", "false").lower() == "true"
MIN_SCORE_AVG = float(os.environ.get("MIN_SCORE_AVG", "6.0"))
LLM_MODEL = os.environ.get("LLM_MODEL", "mimo-v2.5-pro")

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


def merge_papers(existing: list, new_papers: list) -> list:
    """
    合并新旧论文数据。

    规则：
    - 以 title 为唯一标识（不区分大小写）
    - 新数据中已存在的论文会被更新（覆盖）
    - 新数据中不存在的旧论文保留
    """
    existing_by_title = {(p.get("title") or "").lower().strip(): p for p in existing if p.get("title")}

    for paper in new_papers:
        title_key = (paper.get("title") or "").lower().strip()
        if not title_key:
            continue
        if title_key not in existing_by_title:
            max_id = max((p.get("id", 0) for p in existing_by_title.values()), default=0)
            paper["id"] = max_id + 1
        else:
            paper["id"] = existing_by_title[title_key].get("id", 0)
        existing_by_title[title_key] = paper

    merged = list(existing_by_title.values())
    merged.sort(key=lambda p: p.get("date") or "", reverse=True)
    return merged


def compute_composite_score(item: dict) -> dict:
    """为条目计算加权综合分和精选标记"""
    scores = item.get("scores", {})
    if item.get("content_type") == "news":
        composite = round(
            scores.get("timeliness", 0) * 0.3
            + scores.get("relevance", 0) * 0.4
            + scores.get("information_value", 0) * 0.3,
            1,
        )
    else:
        composite = round(
            scores.get("frontier_tech", 0) * WEIGHT_FRONTIER
            + scores.get("practical_value", 0) * WEIGHT_PRACTICAL
            + scores.get("methodological_rigor", 0) * WEIGHT_RIGOR,
            1,
        )
    item["composite_score"] = composite
    item["featured"] = composite >= FEATURED_THRESHOLD
    return item


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
    print(f"[main] BiblioRadar 数据更新开始 {datetime.now().isoformat()}")
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
            compute_composite_score(item)

        merged = merge_papers(existing, evaluated)

        if len(merged) > MAX_TOTAL_ITEMS:
            merged = merged[:MAX_TOTAL_ITEMS]
            print(f"[main] 裁剪至 {MAX_TOTAL_ITEMS} 条")

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = OUTPUT_PATH.with_suffix(".json.tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)
        tmp_path.replace(OUTPUT_PATH)
        print(f"[main] 已写入 {len(merged)} 条到 {OUTPUT_PATH}")
    else:
        print(f"[main] 无新条目需要写入")

    # 第五步：生成日报（基于当天抓取的全部内容，不仅是新增的）
    today_str = datetime.now().strftime("%Y-%m-%d")
    report_items = evaluated if evaluated else raw_papers + raw_news
    print(f"[main] 生成 {today_str} 日报（基于 {len(report_items)} 条）...")
    report = generate_daily_report(report_items, model=LLM_MODEL)
    if report:
        reports = load_daily_reports()
        reports = [r for r in reports if r.get("date") != today_str]
        papers_count = sum(1 for i in evaluated if i.get("content_type") == "paper")
        news_count = sum(1 for i in evaluated if i.get("content_type") == "news")
        featured_count = sum(1 for i in evaluated if i.get("featured"))
        reports.append({
            "date": today_str,
            "summary": report["summary"],
            "highlights": report["highlights"],
            "stats": {
                "papers": papers_count,
                "news": news_count,
                "featured": featured_count,
            },
        })
        reports.sort(key=lambda r: r["date"], reverse=True)
        save_daily_reports(reports)
        print(f"[main] 日报已写入 {DAILY_REPORTS_PATH}")
    else:
        print(f"[main] 日报生成失败，跳过")

    print(f"[main] 数据更新完成")


if __name__ == "__main__":
    main()
