"""
大模型评估模块

调用兼容 OpenAI 格式的 API（如 DeepSeek、Claude），
对论文进行多维度打分和分类。
"""

import json
import os
import re
import sys
from typing import Dict, List, Optional
from openai import OpenAI

from data_contract import normalize_category

# Windows 控制台 UTF-8 输出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ============================================================
# System Prompt（核心：控制大模型输出格式和质量）
# ============================================================

SYSTEM_PROMPT = """你是一位图情领域（Library and Information Science）的资深学术评审专家。你的任务是对输入的学术论文进行专业评估。

## 评估维度

请从以下三个维度对论文打分（1-10 分，10 分最高）：

1. **前沿技术度 (frontier_tech)**：论文是否涉及或采用了当前前沿的技术或方法论？例如：大语言模型、知识图谱、深度学习、语义网、区块链存证等。纯传统方法论的研究此项分数较低。

2. **业务落地值 (practical_value)**：论文的研究成果是否具有直接的实践应用价值？能否被图书馆、信息机构、科研管理部门直接采用？纯理论探讨此项分数较低。

3. **方法严谨性 (methodological_rigor)**：论文的研究方法是否规范、严谨？样本量是否充足？是否有多角度验证？方法论存在明显缺陷的论文此项分数较低。

## 来源敏感的评分指引

根据论文来源和内容类型，在评分时注意以下场景：
- 来自 NISO、COUNTER 等标准组织的规范变动或技术报告 → practical_value 打高分（8+），因为标准直接影响行业实践
- 国内高校图书馆的系统开发、阅读大数据分析、服务创新的实战复盘 → practical_value 和 methodological_rigor 给予适当加分
- 国内期刊论文（如《中国图书馆学报》《情报学报》等）→ 评估时考虑国内图情实践场景（如 CALIS 联合编目、机构知识库建设、学科服务创新），不要因研究场景本土化而低估其价值
- 涉及 FAIR 数据原则、开放科学基础设施的论文 → data_management 分类优先，practical_value 适当加分

## 分类

从以下选项中选择一个最匹配的分类：
- 计量与评价：文献计量、研究评价、替代计量、引文分析
- 检索与推荐：信息检索、搜索系统、推荐系统
- 知识组织：知识组织、本体、分类法、元数据标准
- 数据管理：科研数据管理、开放科学、FAIR 原则
- 数字图书馆：数字图书馆、数字保存、机构知识库
- AI应用：LIS 领域的 AI/ML 应用（如 LLM 辅助文献综述、NLP 文本挖掘）
- 用户行为：用户行为、信息寻求、人机交互、可用性
- 学术传播：学术出版、开放获取、同行评审
- 其他：以上都不匹配时使用

## 输出要求

你必须且只能输出以下 JSON 格式，不要输出任何其他内容：

{
  "thinking": "用2-3句话说明你的评分理由，重点指出论文的优势和不足。语言要平实、专业，禁止使用互联网黑话。",
  "category": "从上述分类中选择一个",
  "scores": {
    "frontier_tech": 8,
    "practical_value": 7,
    "methodological_rigor": 8
  },
  "one_sentence_summary": "用一句通俗易懂的中文概括论文的核心发现或贡献，不超过50字。"
}

## 语言规范

- thinking 和 one_sentence_summary 必须使用中文
- 禁止出现"赋能"、"闭环"、"底层逻辑"、"杠杆效应"、"降本增效"等互联网黑话
- 使用学术界通用的专业表述
- 摘要为中文时，thinking 和 one_sentence_summary 必须使用中文"""


NEWS_SYSTEM_PROMPT = """你是一位图情领域（Library and Information Science）的行业资讯分析师。你的任务是对输入的行业资讯进行专业评估。

## 评估维度

请从以下三个维度对资讯打分（1-10 分，10 分最高）：

1. **时效性 (timeliness)**：资讯是否为近期动态？是否具有新闻价值？过时的旧闻分数较低。

2. **领域相关性 (relevance)**：资讯与图书馆学、信息科学、档案学领域的关联程度如何？与图情领域无关的内容分数较低。

3. **信息价值 (information_value)**：资讯是否提供了可操作的见解或有价值的信息？是否能帮助图情从业者了解行业趋势、做出决策？

## 来源敏感的评分指引

根据资讯来源和内容类型，在评分时注意以下场景：
- NISO、COUNTER 等标准组织发布的规范变动 → relevance 和 information_value 打高分（8+），因为标准直接影响图书馆的统计报告和资源管理实践
- 国内机构（CALIS、CADAL、国家图书馆等）的通知和动态 → 评估时关注对国内图书馆业务的实际影响
- 开放获取政策变动（如 Plan S、NIH 数据共享政策）→ information_value 打高分
- 各大图书馆的系统建设案例、服务创新复盘 → information_value 打高分
- 学术出版行业动态（出版商合并、新平台上线）→ relevance 适当评估，不要因商业色彩而低估其对图情机构的影响

## 分类

从以下选项中选择一个最匹配的分类：
- 行业动态：图书馆、信息机构的新闻和事件
- 技术趋势：影响图情领域的新技术和工具
- 政策标准：与信息管理、开放获取、统计规范相关的政策和标准
- 国内动态：国内图书馆界、CALIS/CADAL 等机构的通知和新闻
- 观点评论：行业专家的分析和评论
- 其他：以上都不匹配时使用

## 输出要求

你必须且只能输出以下 JSON 格式，不要输出任何其他内容：

{
  "thinking": "用2-3句话说明你的评分理由。语言要平实、专业，禁止使用互联网黑话。",
  "category": "从上述分类中选择一个",
  "scores": {
    "timeliness": 8,
    "relevance": 7,
    "information_value": 8
  },
  "one_sentence_summary": "用一句通俗易懂的中文概括这条资讯的核心信息，不超过50字。"
}

## 语言规范

- thinking 和 one_sentence_summary 必须使用中文
- 禁止出现"赋能"、"闭环"、"底层逻辑"、"杠杆效应"、"降本增效"等互联网黑话
- 使用平实的专业表述
- 摘要为中文时，thinking 和 one_sentence_summary 必须使用中文"""


USER_PROMPT_TEMPLATE = """请评估以下论文：

标题：{title}
摘要：{abstract}
发表日期：{date}
来源：{source}
来源级别：{tier}
学科领域：{field}
机构：{affiliations}

请按照系统提示中的要求输出评估结果 JSON。"""

NEWS_USER_PROMPT_TEMPLATE = """请评估以下行业资讯：

标题：{title}
摘要：{abstract}
发布日期：{date}
来源：{source}
来源级别：{tier}
领域：{field}

请按照系统提示中的要求输出评估结果 JSON。"""


# ============================================================
# LLM 客户端配置
# ============================================================

def create_client() -> OpenAI:
    """创建 OpenAI 兼容的客户端"""
    api_key = os.environ.get("LLM_API_KEY", "")
    base_url = os.environ.get("LLM_BASE_URL", "https://api.deepseek.com")

    if not api_key:
        raise ValueError("请设置 LLM_API_KEY 环境变量")

    return OpenAI(api_key=api_key, base_url=base_url)


def _extract_json(text: str) -> Optional[Dict]:
    """从大模型回复中健壮地提取 JSON 对象"""
    if not text:
        return None

    # 去除 markdown 代码块
    if "```" in text:
        parts = text.split("```")
        # 取中间部分（代码块内容）
        if len(parts) >= 3:
            text = parts[1]
            if text.startswith("json"):
                text = text[4:]

    text = text.strip()

    # 尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 用贪婪匹配提取最外层 JSON 对象
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        # 回退到非贪婪匹配
        match = re.search(r"\{.*?\}", text, re.DOTALL)

    if match:
        candidate = match.group(0)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            # 尝试修复截断的 JSON：逐步补全未闭合的括号
            # 统计需要补全的括号数
            open_braces = candidate.count("{") - candidate.count("}")
            open_brackets = candidate.count("[") - candidate.count("]")

            # 如果最后一个字符不是合理的结尾，先截断到最后一个完整值
            # 尝试去掉不完整的尾部
            for trim in range(len(candidate) - 1, max(len(candidate) - 50, 0), -1):
                trimmed = candidate[:trim]
                # 补全未闭合的括号
                fix = trimmed + '"]' * max(open_brackets, 0) + "}" * max(open_braces, 0)
                try:
                    return json.loads(fix)
                except json.JSONDecodeError:
                    continue

            # 最后尝试简单补全
            for suffix in ['"}', '"}', "}"] * 3:
                try:
                    return json.loads(candidate + suffix)
                except json.JSONDecodeError:
                    continue

    return None


def evaluate_paper(client: OpenAI, paper: Dict, model: str = "mimo-v2.5-pro") -> Optional[Dict]:
    """
    调用大模型评估单篇论文。

    Args:
        client: OpenAI 客户端
        paper: 论文字典，包含 title, abstract, date, link, affiliations, source
        model: 模型名称

    Returns:
        包含 thinking, category, scores, one_sentence_summary 的字典，失败返回 None
    """
    user_prompt = USER_PROMPT_TEMPLATE.format(
        title=paper.get("title", ""),
        abstract=paper.get("abstract", ""),
        date=paper.get("date", "未知"),
        source=paper.get("source", "未知"),
        tier=paper.get("tier", "未知"),
        field=paper.get("field", "未知"),
        affiliations=paper.get("affiliations", "未知"),
    )

    try:
        # 带重试的 API 调用（处理偶发的空回复）
        content = ""
        for attempt in range(3):
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=2000,
            )
            content = response.choices[0].message.content or ""
            content = content.strip()
            if content:
                break
            print(f"[llm] 第 {attempt + 1} 次尝试返回空内容，重试...")

        result = _extract_json(content)
        if result is None:
            print(f"[llm] JSON 提取失败，原始回复: {content[:200]}")
            return None

        # 基本验证，缺失的可选字段用默认值补齐
        result.setdefault("one_sentence_summary", "暂无摘要")
        result.setdefault("thinking", "")

        required_keys = ("thinking", "category", "scores", "one_sentence_summary")
        if not all(k in result for k in required_keys):
            print(f"[llm] 返回格式缺少必要字段: {result.keys()}")
            return None

        score_keys = ("frontier_tech", "practical_value", "methodological_rigor")
        if not all(k in result["scores"] for k in score_keys):
            print(f"[llm] scores 字段不完整: {result['scores']}")
            return None

        # 验证分数值为有效数字，限制在 1-10 范围
        scores = result["scores"]
        for k in score_keys:
            v = scores.get(k)
            if not isinstance(v, (int, float)):
                print(f"[llm] scores.{k} 值无效: {v}")
                return None
            v = max(1, min(10, v))
            scores[k] = int(v) if isinstance(v, float) and v == int(v) else v

        return result

    except json.JSONDecodeError as e:
        print(f"[llm] JSON 解析失败: {e}")
        return None
    except Exception as e:
        print(f"[llm] API 调用失败: {e}")
        return None


def evaluate_papers(
    papers: List[Dict],
    model: str = "mimo-v2.5-pro",
    min_score_avg: float = 6.0,
) -> List[Dict]:
    """
    批量评估论文，返回高分论文（含评估结果）。
    """
    client = create_client()
    passed_papers = []

    for i, paper in enumerate(papers):
        print(f"[llm] 评估论文 {i + 1}/{len(papers)}: {paper['title'][:40]}...")

        evaluation = evaluate_paper(client, paper, model=model)
        if not evaluation:
            print(f"[llm] 跳过（评估失败）")
            continue

        scores_vals = [v for v in evaluation["scores"].values() if isinstance(v, (int, float))]
        if len(scores_vals) != 3:
            print(f"[llm] 跳过（分数值异常）")
            continue
        avg_score = sum(scores_vals) / 3
        if avg_score < min_score_avg:
            print(f"[llm] 跳过（平均分 {avg_score:.1f} < {min_score_avg}）")
            continue

        enriched = {
            **paper,
            "content_type": "paper",
            "category": normalize_category(evaluation["category"], "paper"),
            "thinking": evaluation["thinking"],
            "scores": evaluation["scores"],
            "one_sentence_summary": evaluation["one_sentence_summary"],
        }
        passed_papers.append(enriched)
        print(f"[llm] 通过（平均分 {avg_score:.1f}）")

    return passed_papers


def evaluate_news_single(client: OpenAI, item: Dict, model: str = "mimo-v2.5-pro") -> Optional[Dict]:
    """调用大模型评估单条资讯"""
    user_prompt = NEWS_USER_PROMPT_TEMPLATE.format(
        title=item.get("title", ""),
        abstract=item.get("abstract", ""),
        date=item.get("date", "未知"),
        source=item.get("source", "未知"),
        tier=item.get("tier", "未知"),
        field=item.get("field", "未知"),
    )

    try:
        content = ""
        for attempt in range(3):
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": NEWS_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=1500,
            )
            content = response.choices[0].message.content or ""
            content = content.strip()
            if content:
                break
            print(f"[llm] 第 {attempt + 1} 次尝试返回空内容，重试...")

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

        score_keys = ("timeliness", "relevance", "information_value")
        if not all(k in result["scores"] for k in score_keys):
            print(f"[llm] scores 字段不完整: {result['scores']}")
            return None

        scores = result["scores"]
        for k in score_keys:
            v = scores.get(k)
            if not isinstance(v, (int, float)):
                print(f"[llm] scores.{k} 值无效: {v}")
                return None
            v = max(1, min(10, v))
            scores[k] = int(v) if isinstance(v, float) and v == int(v) else v

        return result

    except Exception as e:
        print(f"[llm] API 调用失败: {e}")
        return None


def evaluate_news(
    items: List[Dict],
    model: str = "mimo-v2.5-pro",
    min_score_avg: float = 5.0,
) -> List[Dict]:
    """批量评估资讯，返回通过筛选的条目"""
    client = create_client()
    passed = []

    for i, item in enumerate(items):
        print(f"[llm] 评估资讯 {i + 1}/{len(items)}: {item['title'][:40]}...")

        evaluation = evaluate_news_single(client, item, model=model)
        if not evaluation:
            print(f"[llm] 跳过（评估失败）")
            continue

        scores_vals = [v for v in evaluation["scores"].values() if isinstance(v, (int, float))]
        if len(scores_vals) != 3:
            print(f"[llm] 跳过（分数值异常）")
            continue
        avg_score = sum(scores_vals) / 3
        if avg_score < min_score_avg:
            print(f"[llm] 跳过（平均分 {avg_score:.1f} < {min_score_avg}）")
            continue

        enriched = {
            **item,
            "content_type": "news",
            "category": normalize_category(evaluation["category"], "news"),
            "thinking": evaluation["thinking"],
            "scores": evaluation["scores"],
            "one_sentence_summary": evaluation["one_sentence_summary"],
        }
        passed.append(enriched)
        print(f"[llm] 通过（平均分 {avg_score:.1f}）")

    return passed


# ============================================================
# 日报生成
# ============================================================

DAILY_REPORT_SYSTEM_PROMPT = """你是图情领域的行业分析师。根据今日收录的精选文献和资讯，生成一份简洁的日报摘要。

要求：
- summary: 200-300字，概述今日图情领域的主要发现和趋势
- highlights: 3-5个要点，每个不超过30字
- 使用中文，禁止互联网黑话（赋能、闭环、底层逻辑、杠杆效应、降本增效等）
- 使用学术界通用的专业表述

你必须且只能输出以下 JSON 格式，不要输出任何其他内容：

{
  "summary": "今日图情领域...",
  "highlights": ["要点1", "要点2", "要点3"]
}"""


def generate_daily_report(
    items: List[Dict], model: str = "mimo-v2.5-pro"
) -> Optional[Dict]:
    """
    根据当天条目生成日报摘要。

    Args:
        items: 当天评估通过的条目列表
        model: 模型名称

    Returns:
        包含 summary 和 highlights 的字典，失败返回 None
    """
    if not items:
        return None

    client = create_client()

    papers = [i for i in items if i.get("content_type") == "paper"]
    news = [i for i in items if i.get("content_type") == "news"]
    featured = [i for i in items if i.get("featured")]

    # 优先用精选条目，最多取 15 条避免 prompt 过长
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
        content = ""
        for attempt in range(3):
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": DAILY_REPORT_SYSTEM_PROMPT + "\n\n" + user_prompt},
                ],
                temperature=0.5,
                max_tokens=1000,
            )
            content = response.choices[0].message.content or ""
            content = content.strip()
            if content:
                break
            print(f"[llm] 日报生成第 {attempt + 1} 次尝试返回空内容，重试...")

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


if __name__ == "__main__":
    # 测试：用 mock 数据评估
    from scraper import fetch_mock_papers

    papers = fetch_mock_papers()
    print(f"共 {len(papers)} 篇待评估")

    # 注意：运行前需设置 LLM_API_KEY 环境变量
    # result = evaluate_papers(papers)
    # print(json.dumps(result, ensure_ascii=False, indent=2))
