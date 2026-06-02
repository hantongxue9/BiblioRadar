"""
图情雷达（BiblioRadar）大模型评估模块。

调用兼容 OpenAI 格式的 API，对论文和资讯进行多维度打分与分类。
Prompt 模板从 backend/prompts/ 目录加载，修改评分标准无需改代码。
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional
from openai import OpenAI

try:
    from data_contract import normalize_category
except ImportError:  # pragma: no cover - used when imported as backend.llm_evaluator
    from .data_contract import normalize_category

# Windows 控制台 UTF-8 输出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ============================================================
# Prompt 模板加载
# ============================================================

_PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


def _load_prompt(filename: str) -> str:
    """从 prompts/ 目录加载模板文件。"""
    path = _PROMPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt 模板不存在: {path}")
    return path.read_text(encoding="utf-8").strip()


def _get_system_prompt(for_type: str) -> str:
    """按内容类型加载 system prompt（模块级缓存）。"""
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
    """创建 OpenAI 兼容的客户端。"""
    api_key = api_key or os.environ.get("LLM_API_KEY", "")
    base_url = base_url or os.environ.get("LLM_BASE_URL", "https://api.deepseek.com")
    if not api_key:
        raise ValueError("请设置 LLM_API_KEY 环境变量")
    return OpenAI(api_key=api_key, base_url=base_url)


# ============================================================
# JSON 提取
# ============================================================

def _extract_json(text: str) -> Optional[Dict]:
    """从大模型回复中健壮地提取 JSON 对象。"""
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
    """校验并修正分数值（1-10 范围）。"""
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
    """调用 LLM API，带 3 次重试。"""
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
        print(f"[llm] 第 {attempt + 1} 次尝试返回空内容，重试...")
    return None


def _evaluate_single(client: OpenAI, item: dict, content_type: str,
                     model: str) -> Optional[Dict]:
    """通用单条评估逻辑。"""
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
            print(f"[llm] JSON 提取失败，原始回复: {content[:200]}")
            return None

        result.setdefault("one_sentence_summary", "暂无摘要")
        result.setdefault("thinking", "")

        required_keys = ("thinking", "category", "scores", "one_sentence_summary")
        if not all(k in result for k in required_keys):
            print(f"[llm] 返回格式缺少必要字段: {result.keys()}")
            return None

        score_keys = (
            ("frontier_tech", "practical_value", "methodological_rigor")
            if content_type == "paper"
            else ("timeliness", "relevance", "information_value")
        )
        if not all(k in result["scores"] for k in score_keys):
            print(f"[llm] scores 字段不完整: {result['scores']}")
            return None

        return _validate_scores(result, score_keys)

    except Exception as e:
        print(f"[llm] API 调用失败: {e}")
        return None


# ============================================================
# 批量评估
# ============================================================

def _batch_evaluate(items: List[Dict], content_type: str,
                    model: str, min_score_avg: float) -> List[Dict]:
    """通用批量评估逻辑。"""
    api_key = os.environ.get("LLM_API_KEY", "")
    base_url = os.environ.get("LLM_BASE_URL", "https://api.deepseek.com")
    client = create_client(api_key, base_url)
    label = "论文" if content_type == "paper" else "资讯"
    passed = []

    for i, item in enumerate(items):
        print(f"[llm] 评估{label} {i + 1}/{len(items)}: {item['title'][:40]}...")

        evaluation = _evaluate_single(client, item, content_type, model)
        if not evaluation:
            print(f"[llm] 跳过（评估失败）")
            continue

        scores_vals = [v for v in evaluation["scores"].values()
                       if isinstance(v, (int, float))]
        if len(scores_vals) != 3:
            print(f"[llm] 跳过（分数值异常）")
            continue

        avg_score = sum(scores_vals) / 3
        if avg_score < min_score_avg:
            print(f"[llm] 跳过（平均分 {avg_score:.1f} < {min_score_avg}）")
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
        print(f"[llm] 通过（平均分 {avg_score:.1f}）")

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

def generate_daily_report(items: List[Dict],
                          model: str = "mimo-v2.5-pro") -> Optional[Dict]:
    """根据当天条目生成日报摘要。"""
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
            return None

        result = _extract_json(content)
        if result is None:
            print(f"[llm] 日报 JSON 提取失败，原始回复: {content[:200]}")
            return None

        if "summary" not in result or "highlights" not in result:
            print(f"[llm] 日报缺少必要字段: {result.keys()}")
            return None

        if not isinstance(result["summary"], str) or not isinstance(result["highlights"], list):
            print(f"[llm] 日报字段类型错误")
            return None

        return result

    except Exception as e:
        print(f"[llm] 日报生成失败: {e}")
        return None
