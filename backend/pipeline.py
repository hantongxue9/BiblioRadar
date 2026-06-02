"""
BiblioRadar 数据更新流程模块。

纯逻辑函数，从 config 注入参数，便于测试。
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import List

try:
    from zoneinfo import ZoneInfo
    _HAVE_ZONEINFO = True
except ImportError:
    _HAVE_ZONEINFO = False
    ZoneInfo = None  # type: ignore

try:
    from data_contract import validate_items
    from pipeline_utils import (
        build_report_stats,
        compute_composite_score,
        merge_items,
        prune_reports_to_data_dates,
    )
except ImportError:  # pragma: no cover - used when imported as backend.pipeline
    from .data_contract import validate_items
    from .pipeline_utils import (
        build_report_stats,
        compute_composite_score,
        merge_items,
        prune_reports_to_data_dates,
    )

logger = logging.getLogger("biblioradar.pipeline")


def fetch_all_async(*args, **kwargs):
    try:
        from scraper import fetch_all_async as fn
    except ImportError:  # pragma: no cover
        from .scraper import fetch_all_async as fn
    return fn(*args, **kwargs)


def fetch_mock_papers(*args, **kwargs):
    try:
        from scraper import fetch_mock_papers as fn
    except ImportError:  # pragma: no cover
        from .scraper import fetch_mock_papers as fn
    return fn(*args, **kwargs)


def fetch_mock_news(*args, **kwargs):
    try:
        from scraper import fetch_mock_news as fn
    except ImportError:  # pragma: no cover
        from .scraper import fetch_mock_news as fn
    return fn(*args, **kwargs)


def evaluate_papers(*args, **kwargs):
    try:
        from llm_evaluator import evaluate_papers as fn
    except ImportError:  # pragma: no cover
        from .llm_evaluator import evaluate_papers as fn
    return fn(*args, **kwargs)


def evaluate_news(*args, **kwargs):
    try:
        from llm_evaluator import evaluate_news as fn
    except ImportError:  # pragma: no cover
        from .llm_evaluator import evaluate_news as fn
    return fn(*args, **kwargs)


def generate_daily_report(*args, **kwargs):
    try:
        from llm_evaluator import generate_daily_report as fn
    except ImportError:  # pragma: no cover
        from .llm_evaluator import generate_daily_report as fn
    return fn(*args, **kwargs)


def _load_json(path) -> list:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            return []
    return []


def _save_json(path, data: list):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def run_pipeline(cfg) -> bool:
    """执行完整的数据更新流程，返回是否成功。"""
    logger.info("BiblioRadar 数据更新开始")
    logger.info("输出路径: %s", cfg.output_path)

    existing = _load_json(cfg.output_path)
    existing_titles = {p["title"].lower().strip() for p in existing}

    # 第一步：抓取
    if cfg.use_mock:
        logger.info("使用 mock 数据")
        raw_papers = fetch_mock_papers()
        raw_news = fetch_mock_news()
    else:
        logger.info("从信源池异步抓取")
        raw_papers, raw_news = asyncio.run(
            fetch_all_async(apply_affiliation_filter=cfg.filter_affiliation)
        )

    new_papers = [p for p in raw_papers if p["title"].lower().strip() not in existing_titles]
    new_news = [n for n in raw_news if n["title"].lower().strip() not in existing_titles]
    logger.info("新论文 %d 篇，新资讯 %d 条", len(new_papers), len(new_news))

    evaluated = []  # type: List[dict]
    merged = existing

    # 第二步：评估论文
    if new_papers:
        logger.info("开始评估 %d 篇论文", len(new_papers))
        eval_papers = evaluate_papers(
            new_papers,
            model=cfg.llm_model,
            min_score_avg=cfg.min_score_avg_paper,
        )
        evaluated.extend(eval_papers)
        logger.info("论文通过 %d 篇", len(eval_papers))

    # 第三步：评估资讯
    if new_news:
        logger.info("开始评估 %d 条资讯", len(new_news))
        eval_news = evaluate_news(
            new_news,
            model=cfg.llm_model,
            min_score_avg=cfg.min_score_avg_news,
        )
        evaluated.extend(eval_news)
        logger.info("资讯通过 %d 条", len(eval_news))

    # 第四步：计算综合分并合并写入
    if evaluated:
        for item in evaluated:
            compute_composite_score(
                item,
                featured_threshold=cfg.featured_threshold,
                weight_frontier=cfg.weight_frontier,
                weight_practical=cfg.weight_practical,
                weight_rigor=cfg.weight_rigor,
            )

        merged = merge_items(existing, evaluated)
        if len(merged) > cfg.max_total_items:
            merged = merged[:cfg.max_total_items]
            logger.info("裁剪至 %d 条", cfg.max_total_items)

        validation_errors = validate_items(merged)
        if validation_errors:
            raise ValueError(
                "data.json 契约校验失败:\n" + "\n".join(validation_errors)
            )

        _save_json(cfg.output_path, merged)
        logger.info("已写入 %d 条到 %s", len(merged), cfg.output_path)
    else:
        logger.info("无新条目需要写入")

    # 第五步：生成日报
    from datetime import datetime
    if _HAVE_ZONEINFO:
        today_str = datetime.now(ZoneInfo(cfg.app_timezone)).strftime("%Y-%m-%d")
    else:
        today_str = datetime.now().strftime("%Y-%m-%d")
    reports = prune_reports_to_data_dates(_load_json(cfg.daily_reports_path), merged)

    if not evaluated:
        _save_json(cfg.daily_reports_path, reports)
        logger.info("无新评估通过条目，跳过日报生成")
        logger.info("数据更新完成")
        return True

    report_items = evaluated
    logger.info("生成 %s 日报（基于 %d 条已入库条目）", today_str, len(report_items))

    report = generate_daily_report(report_items, model=cfg.llm_model)
    if report:
        reports = [r for r in reports if r.get("date") != today_str]
        reports.append({
            "date": today_str,
            "summary": report["summary"],
            "highlights": report["highlights"],
            "stats": build_report_stats(report_items),
        })
        reports.sort(key=lambda r: r["date"], reverse=True)
        _save_json(cfg.daily_reports_path, reports)
        logger.info("日报已写入 %s", cfg.daily_reports_path)
    else:
        logger.warning("日报生成失败，跳过")

    logger.info("数据更新完成")
    return True
