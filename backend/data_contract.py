"""Shared data contract helpers for BiblioRadar items."""

from __future__ import annotations

import re
from typing import Any


PAPER_CATEGORIES = {
    "计量与评价",
    "检索与推荐",
    "知识组织",
    "数据管理",
    "数字图书馆",
    "AI应用",
    "用户行为",
    "学术传播",
    "其他",
}

NEWS_CATEGORIES = {
    "行业动态",
    "技术趋势",
    "政策标准",
    "国内动态",
    "观点评论",
    "其他",
}

PAPER_SCORE_KEYS = ("frontier_tech", "practical_value", "methodological_rigor")
NEWS_SCORE_KEYS = ("timeliness", "relevance", "information_value")

BASE_REQUIRED_FIELDS = (
    "id",
    "title",
    "date",
    "link",
    "source",
    "tier",
    "field",
    "content_type",
    "category",
    "scores",
    "one_sentence_summary",
    "composite_score",
    "featured",
)

_CATEGORY_SEPARATORS = ("：", ":", " - ", "—", "（", "(")
_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

_NOISE_TITLE_EXACT = {
    "cover image",
    "issue information",
    "table of contents",
    "contents",
    "front matter",
    "back matter",
    "editorial board",
    "masthead",
}


def allowed_categories(content_type: str) -> set[str]:
    return NEWS_CATEGORIES if content_type == "news" else PAPER_CATEGORIES


def expected_score_keys(content_type: str) -> tuple[str, ...]:
    return NEWS_SCORE_KEYS if content_type == "news" else PAPER_SCORE_KEYS


def normalize_category(category: Any, content_type: str) -> str:
    """Return a prompt-approved category, keeping compatible prefixed labels stable."""
    text = str(category or "").strip()
    allowed = allowed_categories(content_type)
    if not text:
        return "其他"
    if text in allowed:
        return text
    for sep in _CATEGORY_SEPARATORS:
        head = text.split(sep, 1)[0].strip()
        if head in allowed:
            return head
    for candidate in allowed:
        if candidate != "其他" and text.startswith(candidate):
            return candidate
    return "其他"


def is_noise_title(title: Any) -> bool:
    normalized = " ".join(str(title or "").strip().lower().split())
    if not normalized:
        return True
    return normalized in _NOISE_TITLE_EXACT


def is_noise_item(item: dict[str, Any]) -> bool:
    return is_noise_title(item.get("title"))


def normalize_item_for_output(item: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(item)
    content_type = normalized.get("content_type", "paper")
    normalized["category"] = normalize_category(normalized.get("category"), content_type)
    return normalized


def validate_item(item: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(item, dict):
        return ["item must be an object"]

    for field in BASE_REQUIRED_FIELDS:
        if field not in item or item[field] in (None, ""):
            errors.append(f"missing {field}")

    content_type = item.get("content_type")
    if content_type not in {"paper", "news"}:
        errors.append(f"invalid content_type: {content_type!r}")
        content_type = "paper"

    category = item.get("category")
    if category != normalize_category(category, content_type):
        errors.append(f"invalid category: {category!r}")

    date = item.get("date")
    if date and not _DATE_PATTERN.match(str(date)):
        errors.append(f"invalid date: {date!r}")

    scores = item.get("scores")
    if not isinstance(scores, dict):
        errors.append("scores must be an object")
    else:
        for key in expected_score_keys(content_type):
            value = scores.get(key)
            if not isinstance(value, (int, float)) or not 1 <= value <= 10:
                errors.append(f"invalid score {key}: {value!r}")

    composite = item.get("composite_score")
    if not isinstance(composite, (int, float)) or not 0 <= composite <= 10:
        errors.append(f"invalid composite_score: {composite!r}")

    if not isinstance(item.get("featured"), bool):
        errors.append(f"featured must be bool: {item.get('featured')!r}")

    credit = item.get("credibility_score")
    if credit is not None and (not isinstance(credit, (int, float)) or not 0 <= credit <= 10):
        errors.append(f"invalid credibility_score: {credit!r}")

    return errors


def validate_items(items: list[dict[str, Any]], max_errors: int = 20) -> list[str]:
    errors: list[str] = []
    for index, item in enumerate(items):
        for error in validate_item(item):
            errors.append(f"items[{index}]: {error}")
            if len(errors) >= max_errors:
                return errors
    return errors
