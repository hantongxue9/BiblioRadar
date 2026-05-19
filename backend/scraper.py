"""
RSS/API 文献抓取模块

从图情领域（LIS）的主要学术信息源抓取最新文献元数据。
包含机构清洗过滤逻辑，用于精准筛选目标机构的产出。
"""

import re
import feedparser
from datetime import datetime
from typing import List, Dict, Optional


# ============================================================
# RSS 源配置
# ============================================================

RSS_SOURCES = [
    {
        "name": "arXiv - Digital Libraries",
        "url": "https://rss.arxiv.org/rss/cs.DL",
        "field": "digital_libraries",
    },
    {
        "name": "arXiv - Information Retrieval",
        "url": "https://rss.arxiv.org/rss/cs.IR",
        "field": "information_retrieval",
    },
    {
        "name": "arXiv - Computation & Language",
        "url": "https://rss.arxiv.org/rss/cs.CL",
        "field": "nlp",
    },
    {
        "name": "arXiv - Social Networks",
        "url": "https://rss.arxiv.org/rss/cs.SI",
        "field": "social_networks",
    },
    {
        "name": "Information Processing & Management",
        "url": "https://rss.sciencedirect.com/publication/science/03064573",
        "field": "information_science",
    },
    {
        "name": "Code4Lib Journal",
        "url": "https://journal.code4lib.org/feed",
        "field": "library_technology",
    },
    {
        "name": "First Monday",
        "url": "https://firstmonday.org/ojs/index.php/fm/gateway/plugin/WebFeedGatewayPlugin/rss",
        "field": "internet_society",
    },
]

# 行业资讯源
NEWS_SOURCES = [
    {
        "name": "Scholarly Kitchen",
        "url": "https://scholarlykitchen.sspnet.org/feed/",
        "field": "scholarly_publishing",
    },
    {
        "name": "Infodocket",
        "url": "https://www.infodocket.com/feed/",
        "field": "library_news",
    },
    {
        "name": "LSE Impact Blog",
        "url": "https://blogs.lse.ac.uk/impactofsocialsciences/feed/",
        "field": "academic_impact",
    },
    {
        "name": "SPARC News",
        "url": "https://sparcopen.org/feed/",
        "field": "open_access",
    },
]


# ============================================================
# 机构过滤逻辑（硬核模板）
# ============================================================

# 目标机构匹配模式（中国科学技术大学）
# 使用多种拼写变体确保覆盖率
TARGET_AFFILIATION_PATTERNS = [
    re.compile(r"Univ\s+Sci\s*&\s*Technol.*?China", re.IGNORECASE),
    re.compile(r"University\s+of\s+Science\s+and\s+Technology\s+of\s+China", re.IGNORECASE),
    re.compile(r"USTC", re.IGNORECASE),
    re.compile(r"中国科学技术大学", re.IGNORECASE),
    re.compile(r"中科大", re.IGNORECASE),
]

# 排除混淆项：华中科技大学（HUST）等名称相似的机构
# 这些机构的英文名称包含 "University of Science and Technology" 容易误匹配
EXCLUSION_PATTERNS = [
    re.compile(r"Huazhong", re.IGNORECASE),
    re.compile(r"HUST", re.IGNORECASE),
    re.compile(r"华中科技大学", re.IGNORECASE),
    re.compile(r"华中理工", re.IGNORECASE),
    # 可继续添加其他需要排除的机构
    # re.compile(r"Henan\s+University\s+of\s+Science", re.IGNORECASE),
    # re.compile(r"Shanxi\s+University\s+of\s+Science", re.IGNORECASE),
]


def matches_target_affiliation(affiliation_text: str) -> bool:
    """
    判断机构信息是否匹配目标机构。

    逻辑：
    1. 先检查是否命中排除列表（如华中科技大学）
    2. 再检查是否匹配目标机构模式（如 USTC）
    3. 两步都通过才算匹配成功
    """
    if not affiliation_text:
        return False

    # 第一步：排除混淆项
    for pattern in EXCLUSION_PATTERNS:
        if pattern.search(affiliation_text):
            return False

    # 第二步：匹配目标机构
    for pattern in TARGET_AFFILIATION_PATTERNS:
        if pattern.search(affiliation_text):
            return True

    return False


def filter_by_affiliation(papers: List[Dict]) -> List[Dict]:
    """根据机构信息过滤论文列表"""
    return [p for p in papers if matches_target_affiliation(p.get("affiliations", ""))]


# ============================================================
# 抓取逻辑
# ============================================================

def parse_date(entry) -> Optional[str]:
    """从 RSS entry 中解析日期，返回 YYYY-MM-DD 格式"""
    for attr in ("published_parsed", "updated_parsed"):
        time_struct = getattr(entry, attr, None)
        if time_struct:
            try:
                return datetime(*time_struct[:3]).strftime("%Y-%m-%d")
            except (TypeError, ValueError):
                continue
    return None


def extract_affiliations(entry) -> str:
    """尝试从 RSS entry 中提取机构信息"""
    # 不同 RSS 源的机构信息位置不同，这里做兼容处理
    for field in ("arxiv_affiliation", "author_affiliation", "dc_creator"):
        value = getattr(entry, field, None)
        if value:
            return str(value)

    # 尝试从 summary 或 description 中提取
    summary = getattr(entry, "summary", "") or ""
    description = getattr(entry, "description", "") or ""
    text = summary + " " + description

    # 简单的机构提取：查找 "University" 或 "Institute" 开头的文本
    affiliation_match = re.search(
        r"((?:University|Institute|College|Academy)[^.]*?\.)",
        text,
        re.IGNORECASE,
    )
    return affiliation_match.group(1) if affiliation_match else ""


# LIS 相关关键词预过滤（用于宽泛源如 cs.CL）
# 匹配标题或摘要中包含这些词的论文
LIS_KEYWORDS = re.compile(
    r"\blibrary\b|\blibraries\b|\blibrarian\b|\bcatalogue?\b|\bmetadata\b"
    r"|\bbibliograph\w*|\bbibliometric\w*|\bscientometric\w*|\baltmetric\w*"
    r"|\bcitation\s+\w|\bcitation\s+graph|\bcitation\s+network"
    r"|\binformation\s+retrieval|\bsearch\s+engine"
    r"|\brecommendation\s+system|\brecommender\s+system"
    r"|\bknowledge\s+graph|\bknowledge\s+organization"
    r"|\bontology\b|\btaxonomy\b|\bthesaurus\b"
    r"|\bdigital\s+library|\bdigital\s+preservation"
    r"|\binstitutional\s+repository|\bopen\s+access"
    r"|\bscholarly\s+communication|\bpeer\s+review"
    r"|\bresearch\s+data\s+management|\bFAIR\s+data"
    r"|\bdata\s+management\b|\bdata\s+sharing\b"
    r"|\binformation\s+seeking\b|\bhuman.?computer\s+interaction"
    r"|\busability\s+study|\busability\s+test"
    r"|文献\w*计量|图书\w*馆|情报学|信息检索|知识图谱|本体\w*构建|开放获取|学术传播",
    re.IGNORECASE,
)

# 需要关键词过滤的宽泛源
BROAD_SOURCES = {"arXiv - Computation & Language", "arXiv - Social Networks"}


def is_lis_relevant(paper: Dict) -> bool:
    """快速判断论文是否与图情领域相关"""
    text = paper.get("title", "") + " " + paper.get("abstract", "")
    return bool(LIS_KEYWORDS.search(text))


def fetch_from_source(source: Dict) -> List[Dict]:
    """从单个 RSS 源抓取文献"""
    try:
        feed = feedparser.parse(source["url"])
    except Exception as e:
        print(f"[scraper] 抓取失败 {source['name']}: {e}")
        return []

    papers = []
    for entry in feed.entries:
        paper = {
            "title": getattr(entry, "title", "").strip(),
            "abstract": getattr(entry, "summary", "").strip(),
            "date": parse_date(entry),
            "link": getattr(entry, "link", ""),
            "affiliations": extract_affiliations(entry),
            "source": source["name"],
        }
        if paper["title"]:
            papers.append(paper)

    return papers


def fetch_all_papers(apply_affiliation_filter: bool = True) -> List[Dict]:
    """
    从所有配置的 RSS 源抓取文献。

    Args:
        apply_affiliation_filter: 是否应用机构过滤（默认开启）

    Returns:
        去重后的论文列表
    """
    all_papers = []
    seen_titles = set()

    for source in RSS_SOURCES:
        papers = fetch_from_source(source)
        for paper in papers:
            paper["content_type"] = "paper"
            title_key = paper["title"].lower().strip()
            if title_key in seen_titles:
                continue
            if source["name"] in BROAD_SOURCES and not is_lis_relevant(paper):
                continue
            seen_titles.add(title_key)
            all_papers.append(paper)

    print(f"[scraper] 共抓取 {len(all_papers)} 篇文献")

    if apply_affiliation_filter:
        filtered = filter_by_affiliation(all_papers)
        print(f"[scraper] 机构过滤后剩余 {len(filtered)} 篇")
        return filtered

    return all_papers


def fetch_all_news() -> List[Dict]:
    """从资讯源抓取行业新闻"""
    all_news = []
    seen_titles = set()

    for source in NEWS_SOURCES:
        items = fetch_from_source(source)
        for item in items:
            item["content_type"] = "news"
            item["affiliations"] = ""
            title_key = item["title"].lower().strip()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                all_news.append(item)

    print(f"[scraper] 共抓取 {len(all_news)} 条资讯")
    return all_news


# ============================================================
# Mock 数据（开发/测试用）
# ============================================================

MOCK_PAPERS = [
    {
        "title": "Exploring the Impact of Large Language Models on Academic Literature Review: A Bibliometric Perspective",
        "abstract": "This study investigates the transformative role of Large Language Models (LLMs) in conducting systematic literature reviews within the Library and Information Science domain. Using a mixed-methods approach combining bibliometric analysis with expert interviews, we examined how LLM-assisted workflows affect review efficiency, coverage, and accuracy. Results indicate that LLM integration reduces screening time by approximately 60% while maintaining comparable recall rates to traditional methods.",
        "date": "2026-05-08",
        "link": "https://example.com/paper/1",
        "affiliations": "University of Science and Technology of China, Hefei 230026, China",
        "source": "JASIST",
    },
    {
        "title": "构建面向科研数据管理的本体知识图谱：以大气科学领域为例",
        "abstract": "科研数据的快速增长对数据管理和知识发现提出了新挑战。本研究以大气科学领域为切入点，采用七步法构建了一个领域本体知识图谱，涵盖数据集、变量、观测平台和研究主题四类核心概念。",
        "date": "2026-05-06",
        "link": "https://example.com/paper/2",
        "affiliations": "中国科学技术大学，合肥 230026",
        "source": "arXiv - Digital Libraries",
    },
    {
        "title": "Altmetrics在人文社科研究成果评价中的适用性研究",
        "abstract": "传统基于引用的评价指标在人文社科领域存在滞后性和覆盖面不足的问题。本研究系统收集了2020-2025年间中国人文社科领域的12,000余篇论文及其Altmetrics数据。",
        "date": "2026-05-04",
        "link": "https://example.com/paper/3",
        "affiliations": "University of Science and Technology of China",
        "source": "Scientometrics",
    },
    {
        "title": "Digital Preservation Strategies for Born-Digital Academic Materials",
        "abstract": "Born-digital academic materials present unique preservation challenges. This comparative case study examines the digital preservation strategies employed by three national libraries.",
        "date": "2026-05-02",
        "link": "https://example.com/paper/4",
        "affiliations": "USTC, School of Information Management",
        "source": "JASIST",
    },
]


def fetch_mock_papers() -> List[Dict]:
    """返回 mock 数据，用于开发和测试"""
    return MOCK_PAPERS


MOCK_NEWS = [
    {
        "title": "ALA Annual 2026: Key Takeaways for Library Technology Services",
        "abstract": "The American Library Association's annual conference featured major announcements about AI integration in library services, new digital lending platforms, and updated accessibility standards. Key themes included responsible AI adoption, privacy-first data analytics, and next-generation discovery systems.",
        "date": "2026-05-18",
        "link": "https://example.com/news/1",
        "source": "Scholarly Kitchen",
    },
    {
        "title": "Open Access 2030: European Commission Unveils New Mandate",
        "abstract": "The European Commission has announced a comprehensive open access policy requiring all publicly funded research to be immediately available without embargo. The policy includes provisions for diamond open access journals and mandates data sharing alongside publications.",
        "date": "2026-05-17",
        "link": "https://example.com/news/2",
        "source": "Infodocket",
    },
]


def fetch_mock_news() -> List[Dict]:
    """返回 mock 资讯数据"""
    for item in MOCK_NEWS:
        item["content_type"] = "news"
        item["affiliations"] = ""
    return MOCK_NEWS


if __name__ == "__main__":
    # 测试：打印抓取结果
    papers = fetch_all_papers(apply_affiliation_filter=False)
    for p in papers:
        print(f"  [{p['date']}] {p['title'][:60]}...")
