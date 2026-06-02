"""Pure helpers used by the data update pipeline."""

from __future__ import annotations

from typing import Any

try:
    from data_contract import normalize_category, normalize_item_for_output
except ImportError:  # pragma: no cover - used when imported as backend.pipeline_utils
    from .data_contract import normalize_category, normalize_item_for_output


def merge_items(existing: list[dict[str, Any]], new_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Merge old and new items by normalized title.

    Existing ids are preserved; new items receive monotonically increasing ids.
    """
    existing_by_title = {
        (item.get("title") or "").lower().strip(): normalize_item_for_output(item)
        for item in existing
        if item.get("title")
    }
    next_id = max(
        (
            item.get("id", 0)
            for item in existing_by_title.values()
            if isinstance(item.get("id"), int)
        ),
        default=0,
    ) + 1

    for raw_item in new_items:
        item = normalize_item_for_output(raw_item)
        title_key = (item.get("title") or "").lower().strip()
        if not title_key:
            continue
        if title_key in existing_by_title:
            item["id"] = existing_by_title[title_key].get("id", 0)
        else:
            if not isinstance(item.get("id"), int):
                item["id"] = next_id
                next_id += 1
            else:
                next_id = max(next_id, item["id"] + 1)
        existing_by_title[title_key] = item

    merged = list(existing_by_title.values())
    merged.sort(key=lambda item: item.get("date") or "", reverse=True)
    return merged


def compute_composite_score(
    item: dict[str, Any],
    *,
    featured_threshold: float,
    weight_frontier: float,
    weight_practical: float,
    weight_rigor: float,
) -> dict[str, Any]:
    scores = item.get("scores", {})
    content_type = item.get("content_type")
    item["category"] = normalize_category(item.get("category"), content_type)

    if content_type == "news":
        llm_score = (
            scores.get("timeliness", 0) * 0.3
            + scores.get("relevance", 0) * 0.4
            + scores.get("information_value", 0) * 0.3
        )
    else:
        llm_score = (
            scores.get("frontier_tech", 0) * weight_frontier
            + scores.get("practical_value", 0) * weight_practical
            + scores.get("methodological_rigor", 0) * weight_rigor
        )

    credit = item.get("credibility_score", 5.0)
    composite = round(llm_score * 0.8 + credit * 0.2, 1)

    item["composite_score"] = composite
    item["featured"] = composite >= featured_threshold
    return item


def compute_credibility_score(item: dict[str, Any]) -> float:
    """Rule-based credibility boost — rewards peer-reviewed, complete, high-tier items."""
    credit = 5.0  # baseline

    tier = (item.get("tier") or "").upper()
    if tier == "A":
        credit += 1.0
    elif tier == "B":
        credit += 0.6
    elif tier == "C":
        credit += 0.2

    link = (item.get("link") or "").strip()
    if link and not link.startswith("http"):
        link = ""
    if link:
        # Simple DOI / CrossRef heuristic
        if "doi.org" in link.lower() or "crossref" in link.lower():
            credit += 0.5
        else:
            credit += 0.3

    abstract = (item.get("abstract") or "").strip()
    if len(abstract) >= 50:
        credit += 0.3
    elif abstract:
        credit += 0.1

    summary = (item.get("one_sentence_summary") or "").strip()
    if len(summary) >= 10:
        credit += 0.2

    item["credibility_score"] = round(min(credit, 10.0), 1)
    return item["credibility_score"]


def build_report_stats(items: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "papers": sum(1 for item in items if item.get("content_type") == "paper"),
        "news": sum(1 for item in items if item.get("content_type") == "news"),
        "featured": sum(1 for item in items if item.get("featured")),
    }


def prune_reports_to_data_dates(
    reports: list[dict[str, Any]],
    items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Keep daily reports only for dates still represented in data.json."""
    dates = {item.get("date") for item in items if item.get("date")}
    return [report for report in reports if report.get("date") in dates]
