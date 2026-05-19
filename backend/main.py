"""
Scholar-Radar 后端主入口

调度抓取和评估逻辑，将最终结果写入前端的 public/data.json。
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# 加载项目根目录的 .env 文件
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from scraper import fetch_all_papers, fetch_mock_papers, fetch_all_news, fetch_mock_news
from llm_evaluator import evaluate_papers, evaluate_news


# ============================================================
# 配置
# ============================================================

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "public" / "data.json"

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
    existing_by_title = {p["title"].lower().strip(): p for p in existing}

    for paper in new_papers:
        title_key = paper["title"].lower().strip()
        # 为新论文分配递增 ID
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
        # 资讯用不同的权重
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


def main():
    """主流程：抓取论文 + 资讯 → 评估 → 综合分 → 写入"""
    print(f"[main] Scholar-Radar 数据更新开始 {datetime.now().isoformat()}")
    print(f"[main] 输出路径: {OUTPUT_PATH}")

    # 加载已有数据，用于去重
    existing = load_existing_data()
    existing_titles = {p["title"].lower().strip() for p in existing}

    # 第一步：抓取论文
    if USE_MOCK:
        print("[main] 使用 mock 数据")
        raw_papers = fetch_mock_papers()
        raw_news = fetch_mock_news()
    else:
        print("[main] 从 RSS 源抓取")
        raw_papers = fetch_all_papers(apply_affiliation_filter=FILTER_AFFILIATION)
        raw_news = fetch_all_news()

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

    if not evaluated:
        print("[main] 无新条目需要写入")
        return

    # 第四步：计算综合分
    for item in evaluated:
        compute_composite_score(item)

    # 第五步：合并
    merged = merge_papers(existing, evaluated)

    # 第六步：裁剪（保留最新的 MAX_TOTAL_ITEMS 条）
    if len(merged) > MAX_TOTAL_ITEMS:
        merged = merged[:MAX_TOTAL_ITEMS]
        print(f"[main] 裁剪至 {MAX_TOTAL_ITEMS} 条")

    # 第七步：写入
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    print(f"[main] 已写入 {len(merged)} 条到 {OUTPUT_PATH}")
    print(f"[main] 数据更新完成")


if __name__ == "__main__":
    main()
