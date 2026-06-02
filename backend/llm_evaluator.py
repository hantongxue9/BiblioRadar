"""
图情雷达（BiblioRadar）大模型评估模块。

调用兼容 OpenAI 格式的 API，对论文和资讯进行多维度打分与分类。
Prompt 模板从 backend/prompts/ 目录加载，修改评分标准无需改代码。
"""

import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional
from openai import OpenAI

from .data_contract import normalize_category

logger = logging.getLogger(__name__)

# Windows 控制台 UTF-8 输出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ============================================================
# Prompt 模板加载
# ============================================================

_PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


def _load_prompt(filename: str) -> str:
    path = _PROMPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt 模板不存在: {path}")
    return path.read_text(encoding="utf-8").strip()


def _get_system_prompt(for_type: str) -> str:
    filename = "paper_system.txt" if for_type == "paper" else "news_system.txt"
    return _load_prompt(filename)


def _get_daily_report_prompt() -> str:
    return _load_prompt("daily_report.txt")


# ============================================================
# User prompt 模板
# ============================================================

PAPER_USER_TEMPLATE = """请评估以下论文：

标题：{title}
摘要：{abstract}
发表日期：{date}
来源：{source}
来源级别：{tier}
学科领域：{field}
机构：{affiliations}

请按照系统提示中的要求输出评估结果 JSON。"""

NEWS_USER_TEMPLATE = """请评估以下行业资讯：

标题：{title}
摘要：{abstract}
发布日期：{date}
来源：{source}
来源级别：{tier}
领域：{field}

请按照系统提示中的要求输出评估结果 JSON。"""


# ============================================================
# LLM 客户端
# ============================================================

def create_client(api_key: str = "", base_url: str = "") -> OpenAI:
    api_key = api_key or os.environ.get("LLM_API_KEY", "")
    base_url = base_url or os.environ.get("LLM_BASE_URL", "https://api.deepseek.com")
    if not api_key:
        raise ValueError("请设置 LLM_API_KEY 环境变量")
    return OpenAI(api_key=api_key, base_url=base_url)


# ============================================================
# JSON 提取
# ============================================================

def _extract_json(text: str) -> Optional[Dict]:
    if not text:
        return None

    if "```" in text:
        parts = text.split("```")
        if len(parts) >= 3:
            text = parts[1]
            if text.startswith("json"):
                text = text[4:]

    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        match = re.search(r"\{.*?\}", text, re.DOTALL)

    if match:
        candidate = match.group(0)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            open_braces = candidate.count("{") - candidate.count("}")
            open_brackets = candidate.count("[") - candidate.count("]")
            for trim in range(len(candidate) - 1, max(len(candidate) - 50, 0), -1):
                trimmed = candidate[:trim]
                fix = trimmed + '"]' * max(open_brackets, 0) + "}" * max(open_braces, 0)
                try:
                    return json.loads(fix)
                except json.JSONDecodeError:
                    continue
            for suffix in ['"}', '"}', "}"] * 3:
                try:
                    return json.loads(candidate + suffix)
                except json.JSONDecodeError:
                    continue
    return None


# ============================================================
# 单条评估
# ============================================================

def _validate_scores(result: dict, score_keys: tuple) -> Optional[dict]:
    scores = result.get("scores", {})
    for k in score_keys:
        v = scores.get(k)
        if not isinstance(v, (int, float)):
            return None
        v = max(1, min(10, v))
        scores[k] = int(v) if isinstance(v, float) and v == int(v) else v
    return result


def _call_llm(client: OpenAI, system_prompt: str, user_prompt: str,
              model: str, temperature: float = 0.3,
              max_tokens: int = 2000) -> Optional[str]:
    for attempt in range(3):
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = (response.choices[0].message.content or "").strip()
        if content:
            return content
        logger.warning("第 %d 次尝试返回空内容，重试...", attempt + 1)
    return None


def _evaluate_single(client: OpenAI, item: dict, content_type: str,
                     model: str) -> Optional[Dict]:
    system_prompt = _get_system_prompt(content_type)
    template = PAPER_USER_TEMPLATE if content_type == "paper" else NEWS_USER_TEMPLATE
    max_tokens = 2000 if content_type == "paper" else 1500

    user_prompt = template.format(
        title=item.get("title", ""),
        abstract=item.get("abstract", ""),
        date=item.get("date", "未知"),
        source=item.get("source", "未知"),
        tier=item.get("tier", "未知"),
        field=item.get("field", "未知"),
        **({"affiliations": item.get("affiliations", "未知")} if content_type == "paper" else {}),
    )

    try:
        content = _call_llm(client, system_prompt, user_prompt, model,
                            max_tokens=max_tokens)
        if not content:
            return None

        result = _extract_json(content)
        if result is None:
            logger.warning("JSON 提取失败，原始回复: %s", content[:200])
            return None

        result.setdefault("one_sentence_summary", "暂无摘要")
        result.setdefault("thinking", "")

        required_keys = ("thinking", "category", "scores", "one_sentence_summary")
        if not all(k in result for k in required_keys):
            logger.warning("返回格式缺少必要字段: %s", result.keys())
            return None

        score_keys = (
            ("frontier_tech", "practical_value", "methodological_rigor")
            if content_type == "paper"
            else ("timeliness", "relevance", "information_value")
        )
        if not all(k in result["scores"] for k in score_keys):
            logger.warning("scores 字段不完整: %s", result['scores'])
            return None

        return _validate_scores(result, score_keys)

    except Exception as e:
        logger.error("API 调用失败: %s", e)
        return None


# ============================================================
# 批量评估
# ============================================================

def _batch_evaluate(items: List[Dict], content_type: str,
                    model: str, min_score_avg: float) -> List[Dict]:
    api_key = os.environ.get("LLM_API_KEY", "")
    base_url = os.environ.get("LLM_BASE_URL", "https://api.deepseek.com")
    client = create_client(api_key, base_url)
    label = "论文" if content_type == "paper" else "资讯"
    passed = []

    for i, item in enumerate(items):
        logger.info("评估%s %d/%d: %s", label, i + 1, len(items), item['title'][:40])

        evaluation = _evaluate_single(client, item, content_type, model)
        if not evaluation:
            logger.info("跳过（评估失败）")
            continue

        scores_vals = [v for v in evaluation["scores"].values()
                       if isinstance(v, (int, float))]
        if len(scores_vals) != 3:
            logger.info("跳过（分数值异常）")
            continue

        avg_score = sum(scores_vals) / 3
        if avg_score < min_score_avg:
            logger.info("跳过（平均分 %.1f < %.1f）", avg_score, min_score_avg)
            continue

        enriched = {
            **item,
            "content_type": content_type,
            "category": normalize_category(evaluation["category"], content_type),
            "thinking": evaluation["thinking"],
            "scores": evaluation["scores"],
            "one_sentence_summary": evaluation["one_sentence_summary"],
        }
        passed.append(enriched)
        logger.info("通过（平均分 %.1f）", avg_score)

    return passed


def evaluate_papers(papers: List[Dict], model: str = "mimo-v2.5-pro",
                    min_score_avg: float = 6.0) -> List[Dict]:
    """批量评估论文，返回通过筛选的条目。"""
    return _batch_evaluate(papers, "paper", model, min_score_avg)


def evaluate_news(items: List[Dict], model: str = "mimo-v2.5-pro",
                  min_score_avg: float = 5.0) -> List[Dict]:
    """批量评估资讯，返回通过筛选的条目。"""
    return _batch_evaluate(items, "news", model, min_score_avg)


# ============================================================
# 日报生成
# ============================================================

def _fallback_daily_report(items: List[Dict]) -> Dict:
    """LLM 日报生成失败时的兜底：基于 stats 的纯文本日报。"""
    papers = [i for i in items if i.get("content_type") == "paper"]
    news = [i for i in items if i.get("content_type") == "news"]
    featured = [i for i in items if i.get("featured")]

    lines = [f"今日收录了 {len(papers)} 篇论文和 {len(news)} 条资讯。"]
    if featured:
        lines.append(f"其中 {len(featured)} 篇为精选推荐。")
        lines.append("")
        lines.append("精选条目：")
        for item in featured[:5]:
            lines.append(f"- {item.get('title', '')}")

    return {
        "summary": "\n".join(lines),
        "highlights": [
            f"{item.get('title', '')}"
            for item in (featured if featured else items)[:5]
        ],
    }


def generate_daily_report(items: List[Dict],
                          model: str = "mimo-v2.5-pro") -> Optional[Dict]:
    """根据当天条目生成日报摘要。失败时返回兜底日报。"""
    if not items:
        return None

    api_key = os.environ.get("LLM_API_KEY", "")
    base_url = os.environ.get("LLM_BASE_URL", "https://api.deepseek.com")
    client = create_client(api_key, base_url)

    papers = [i for i in items if i.get("content_type") == "paper"]
    news = [i for i in items if i.get("content_type") == "news"]
    featured = [i for i in items if i.get("featured")]

    report_items = featured if featured else items
    report_items = report_items[:15]

    lines = [f"今日收录 {len(papers)} 篇论文、{len(news)} 条资讯，精选 {len(featured)} 篇。\n"]
    for item in report_items:
        lines.append(
            f"- [{item.get('category', '')}] {item.get('title', '')}："
            f"{item.get('one_sentence_summary', '')}"
        )
    user_prompt = "\n".join(lines)

    try:
        system_prompt = _get_daily_report_prompt()
        content = _call_llm(client, system_prompt, user_prompt, model,
                            temperature=0.5, max_tokens=1000)
        if not content:
            logger.warning("日报 LLM 返回空，使用兜底日报")
            return _fallback_daily_report(items)

        result = _extract_json(content)
        if result is None:
            logger.warning("日报 JSON 提取失败，使用兜底日报")
            return _fallback_daily_report(items)

        if "summary" not in result or "highlights" not in result:
            logger.warning("日报缺少必要字段，使用兜底日报")
            return _fallback_daily_report(items)

        if not isinstance(result["summary"], str) or not isinstance(result["highlights"], list):
            logger.warning("日报字段类型错误，使用兜底日报")
            return _fallback_daily_report(items)

        return result

    except Exception as e:
        logger.error("日报生成失败: %s，使用兜底日报", e)
        return _fallback_daily_report(items)