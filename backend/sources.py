"""
信源配置模块

集中管理所有学术期刊、行业资讯、政策动态的抓取源。
每个源按 A/B/C 三级分类，配置抓取方式（RSS/Web/API）和元数据字段。
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SourceConfig:
    """单个信源的完整配置"""
    name: str               # 信源显示名称
    url: str                # 抓取地址
    tier: str               # 分级：A（核心期刊）/ B（国内权威）/ C（行业动态）
    content_type: str       # paper / news / policy
    field: str              # 学科领域标签
    fetch_method: str       # rss / web / api
    enabled: bool = True    # 是否启用
    extra: dict = field(default_factory=dict)  # 扩展参数（如 CSS 选择器）


# ============================================================
# A类：国际图情核心期刊（T1）
# ============================================================

A_SOURCES = [
    SourceConfig(
        name="Scientometrics",
        url="https://link.springer.com/search.rss?query=&search-within=Journal&facet-journal-id=11192",
        tier="A",
        content_type="paper",
        field="bibliometrics",
        fetch_method="rss",
    ),
    SourceConfig(
        name="JASIST",
        url="https://api.crossref.org/journals/2330-1635/works?rows=20&sort=published&order=desc",
        tier="A",
        content_type="paper",
        field="information_science",
        fetch_method="api",
        extra={"api_type": "crossref", "issn": "2330-1635"},
    ),
    SourceConfig(
        name="Journal of Informetrics",
        url="https://rss.sciencedirect.com/publication/science/17511577",
        tier="A",
        content_type="paper",
        field="bibliometrics",
        fetch_method="rss",
    ),
    SourceConfig(
        name="Library & Information Science Research",
        url="https://rss.sciencedirect.com/publication/science/07408188",
        tier="A",
        content_type="paper",
        field="library_science",
        fetch_method="rss",
    ),
    SourceConfig(
        name="Information Processing & Management",
        url="https://rss.sciencedirect.com/publication/science/03064573",
        tier="A",
        content_type="paper",
        field="information_science",
        fetch_method="rss",
    ),
    SourceConfig(
        name="The Electronic Library",
        url="https://api.crossref.org/journals/0264-0473/works?rows=20&sort=published&order=desc",
        tier="A",
        content_type="paper",
        field="library_technology",
        fetch_method="api",
        extra={"api_type": "crossref", "issn": "0264-0473"},
    ),
]

# ============================================================
# B类：国内权威图情期刊（T1.5）
# 通过知网期刊页抓取最新目录
# ============================================================

B_SOURCES = [
    SourceConfig(
        name="中国图书馆学报",
        url="https://navi.cnki.net/knavi/journals/ZTQG/detail",
        tier="B",
        content_type="paper",
        field="library_science",
        fetch_method="web",
        extra={
            "cnki_code": "ZTQG",
            "selectors": {
                "item_list": ".article-list .row",
                "title": ".title a",
                "author": ".author",
                "abstract": ".abstract",
            },
        },
    ),
    SourceConfig(
        name="大学图书馆学报",
        url="https://navi.cnki.net/knavi/journals/DXTS/detail",
        tier="B",
        content_type="paper",
        field="academic_library",
        fetch_method="web",
        extra={
            "cnki_code": "DXTS",
            "selectors": {
                "item_list": ".article-list .row",
                "title": ".title a",
                "author": ".author",
                "abstract": ".abstract",
            },
        },
    ),
    SourceConfig(
        name="图书情报工作",
        url="https://navi.cnki.net/knavi/journals/TSQB/detail",
        tier="B",
        content_type="paper",
        field="information_science",
        fetch_method="web",
        extra={
            "cnki_code": "TSQB",
            "selectors": {
                "item_list": ".article-list .row",
                "title": ".title a",
                "author": ".author",
                "abstract": ".abstract",
            },
        },
    ),
    SourceConfig(
        name="情报学报",
        url="https://navi.cnki.net/knavi/journals/QBXB/detail",
        tier="B",
        content_type="paper",
        field="information_science",
        fetch_method="web",
        extra={
            "cnki_code": "QBXB",
            "selectors": {
                "item_list": ".article-list .row",
                "title": ".title a",
                "author": ".author",
                "abstract": ".abstract",
            },
        },
    ),
]

# ============================================================
# C类：行业动态、政策与预印本（T2）
# ============================================================

# C类 - 预印本（已有）
C_ARXIV_SOURCES = [
    SourceConfig(
        name="arXiv - Digital Libraries",
        url="https://rss.arxiv.org/rss/cs.DL",
        tier="C",
        content_type="paper",
        field="digital_libraries",
        fetch_method="rss",
    ),
    SourceConfig(
        name="arXiv - Information Retrieval",
        url="https://rss.arxiv.org/rss/cs.IR",
        tier="C",
        content_type="paper",
        field="information_retrieval",
        fetch_method="rss",
    ),
    SourceConfig(
        name="arXiv - Computation & Language",
        url="https://rss.arxiv.org/rss/cs.CL",
        tier="C",
        content_type="paper",
        field="nlp",
        fetch_method="rss",
    ),
    SourceConfig(
        name="arXiv - Social Networks",
        url="https://rss.arxiv.org/rss/cs.SI",
        tier="C",
        content_type="paper",
        field="social_networks",
        fetch_method="rss",
    ),
]

# C类 - API 数据库（开放学术数据源）
C_API_PAPER_SOURCES = [
    SourceConfig(
        name="OpenAlex - LIS",
        url="https://api.openalex.org/works",
        tier="C",
        content_type="paper",
        field="information_science",
        fetch_method="api",
        extra={"api_type": "openalex"},
    ),
    SourceConfig(
        name="Semantic Scholar - LIS",
        url="https://api.semanticscholar.org/graph/v1/paper/search",
        tier="C",
        content_type="paper",
        field="information_science",
        fetch_method="api",
        extra={"api_type": "semantic_scholar"},
    ),
]

# C类 - 国际政策与联盟
C_POLICY_SOURCES = [
    SourceConfig(
        name="NISO News",
        url="https://www.niso.org/news",
        tier="C",
        content_type="news",
        field="standards",
        fetch_method="web",
        extra={
            "selectors": {
                "item_list": ".view-content .views-row, .item-list li, article, .news-item",
                "title": "h3 a, h2 a, .title a",
                "date": ".date-display-single, time, .date",
                "summary": ".field-content, .summary, p",
            },
        },
    ),
    SourceConfig(
        name="LIBER News",
        url="https://libereurope.eu/news/",
        tier="C",
        content_type="news",
        field="library_policy",
        fetch_method="web",
        extra={
            "selectors": {
                "item_list": ".post-item",
                "title": ".post-item__title a",
                "date": ".post-item__date",
                "summary": ".post-item__excerpt",
            },
        },
    ),
    SourceConfig(
        name="ARL News",
        url="https://www.arl.org/news/",
        tier="C",
        content_type="news",
        field="research_library",
        fetch_method="web",
        extra={
            "selectors": {
                "item_list": ".views-row",
                "title": ".views-field-title a",
                "date": ".views-field-created",
                "summary": ".views-field-body",
            },
        },
    ),
]

# C类 - 行业资讯（已有）
C_NEWS_SOURCES = [
    SourceConfig(
        name="Scholarly Kitchen",
        url="https://scholarlykitchen.sspnet.org/feed/",
        tier="C",
        content_type="news",
        field="scholarly_publishing",
        fetch_method="rss",
    ),
    SourceConfig(
        name="Infodocket",
        url="https://www.infodocket.com/feed/",
        tier="C",
        content_type="news",
        field="library_news",
        fetch_method="rss",
    ),
    SourceConfig(
        name="LSE Impact Blog",
        url="https://blogs.lse.ac.uk/impactofsocialsciences/feed/",
        tier="C",
        content_type="news",
        field="academic_impact",
        fetch_method="rss",
    ),
    SourceConfig(
        name="SPARC News",
        url="https://sparcopen.org/feed/",
        tier="C",
        content_type="news",
        field="open_access",
        fetch_method="rss",
    ),
    SourceConfig(
        name="Code4Lib Journal",
        url="https://journal.code4lib.org/feed",
        tier="C",
        content_type="news",
        field="library_technology",
        fetch_method="rss",
    ),
    SourceConfig(
        name="First Monday",
        url="https://firstmonday.org/ojs/index.php/fm/gateway/plugin/WebFeedGatewayPlugin/rss",
        tier="C",
        content_type="news",
        field="internet_society",
        fetch_method="rss",
    ),
]

# C类 - 国内机构动态
C_DOMESTIC_SOURCES = [
    SourceConfig(
        name="CALIS 通知",
        url="https://www.calis.edu.cn/",
        tier="C",
        content_type="news",
        field="domestic_library",
        fetch_method="web",
        extra={
            "selectors": {
                "item_list": ".news-list li",
                "title": "a",
                "date": ".date",
            },
        },
    ),
    SourceConfig(
        name="CADAL 通知",
        url="https://www.cadal.cn/",
        tier="C",
        content_type="news",
        field="digital_library",
        fetch_method="web",
        extra={
            "selectors": {
                "item_list": ".news-item",
                "title": "a",
                "date": ".date",
            },
        },
    ),
]


# ============================================================
# 汇总：所有启用的源
# ============================================================

def get_all_sources() -> list[SourceConfig]:
    """返回所有启用的源配置"""
    all_sources = A_SOURCES + B_SOURCES + C_ARXIV_SOURCES + C_API_PAPER_SOURCES + C_POLICY_SOURCES + C_NEWS_SOURCES + C_DOMESTIC_SOURCES
    return [s for s in all_sources if s.enabled]


def get_paper_sources() -> list[SourceConfig]:
    """返回所有论文类源"""
    return [s for s in get_all_sources() if s.content_type == "paper"]


def get_news_sources() -> list[SourceConfig]:
    """返回所有资讯/政策类源"""
    return [s for s in get_all_sources() if s.content_type in ("news", "policy")]


# 宽泛源：需要 LIS 关键词预过滤的源
BROAD_SOURCE_NAMES = {
    "arXiv - Computation & Language",
    "arXiv - Social Networks",
    "OpenAlex - LIS",
    "Semantic Scholar - LIS",
}
