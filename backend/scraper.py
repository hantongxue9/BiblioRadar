"""异步文献抓取引擎.

从配置的信源池并发抓取文献元数据。
支持 RSS、Web 页面、出版商 API 三种抓取方式。
内置域名级限流、指数退避重试、UA 伪装，适配校园网环境。
"""

from __future__ import annotations

import asyncio
import logging
import os
import random
import re
import sys
import time
from typing import Optional
from urllib.parse import urlparse

# Windows 控制台 UTF-8 输出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import aiohttp
import feedparser
from bs4 import BeautifulSoup

from .sources import (
    SourceConfig,
    BROAD_SOURCE_NAMES,
    get_paper_sources,
    get_news_sources,
    get_all_sources,
)
from .data_contract import is_noise_item

logger = logging.getLogger(__name__)

# ============================================================
# User-Agent 池与请求头
# ============================================================

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 OPR/112.0.0.0",
]


def _random_headers(referer: str = "") -> dict:
    """生成随机请求头"""
    headers = {
        "User-Agent": random.choice(_USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }
    if referer:
        headers["Referer"] = referer
    return headers


# ============================================================
# 域名级限流器
# ============================================================

class RateLimiter:
    """按域名维护请求间隔，防止触发反爬"""

    def __init__(self, min_delay: float = 3.0, max_delay: float = 8.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self._last_request: dict[str, float] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    def _get_lock(self, domain: str) -> asyncio.Lock:
        if domain not in self._locks:
            self._locks[domain] = asyncio.Lock()
        return self._locks[domain]

    async def acquire(self, domain: str):
        """等待直到可以对该域名发起请求"""
        lock = self._get_lock(domain)
        async with lock:
            now = time.monotonic()
            if domain in self._last_request:
                elapsed = now - self._last_request[domain]
                delay = random.uniform(self.min_delay, self.max_delay)
                if elapsed < delay:
                    await asyncio.sleep(delay - elapsed)
            self._last_request[domain] = time.monotonic()


# ============================================================
# 带重试的 HTTP 请求
# ============================================================

REQUEST_TIMEOUT = 30
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
SSL_VERIFY = os.getenv("DISABLE_SSL_VERIFY", "false").lower() != "true"


async def _fetch_url(
    session: aiohttp.ClientSession,
    url: str,
    rate_limiter: RateLimiter,
) -> Optional[str]:
    """
    发起带限流和重试的 GET 请求。

    返回响应文本，失败返回 None。
    """
    domain = urlparse(url).netloc
    last_err = None

    for attempt in range(MAX_RETRIES):
        await rate_limiter.acquire(domain)
        try:
            timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
            async with session.get(
                url,
                headers=_random_headers(referer=f"https://{domain}/"),
                timeout=timeout,
                ssl=SSL_VERIFY,
            ) as resp:
                if resp.status == 429:
                    retry_after = int(resp.headers.get("Retry-After", 10))
                    logger.warning("429 限流，等待 %ds: %s", retry_after, url)
                    await asyncio.sleep(retry_after)
                    continue
                if resp.status in (503, 502, 500):
                    wait = 2 ** (attempt + 1)
                    logger.warning("HTTP %d，%ds 后重试: %s", resp.status, wait, url)
                    await asyncio.sleep(wait)
                    continue
                if resp.status != 200:
                    logger.warning("HTTP %d: %s", resp.status, url)
                    return None
                return await resp.text()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            last_err = e
            wait = 2 ** (attempt + 1)
            logger.warning("请求异常 (%s)，%ds 后重试: %s", e, wait, url)
            await asyncio.sleep(wait)

    logger.error("重试耗尽，放弃: %s (最后错误: %s)", url, last_err)
    return None


# ============================================================
# 日期解析
# ============================================================

def _parse_date(entry) -> Optional[str]:
    """从 feedparser entry 解析日期"""
    for attr in ("published_parsed", "updated_parsed"):
        time_struct = getattr(entry, attr, None)
        if time_struct:
            try:
                from datetime import datetime
                return datetime(*time_struct[:3]).strftime("%Y-%m-%d")
            except (TypeError, ValueError):
                continue
    return None


def _parse_date_str(date_str: str) -> Optional[str]:
    """尝试从字符串解析日期为 YYYY-MM-DD 格式"""
    if not date_str:
        return None
    from datetime import datetime
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日", "%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    # 尝试提取 YYYY-MM-DD 子串
    m = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", date_str)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    return None


# ============================================================
# 机构过滤（USTC）
# ============================================================

TARGET_AFFILIATION_PATTERNS = [
    re.compile(r"Univ\s+Sci\s*&\s*Technol.*?China", re.IGNORECASE),
    re.compile(r"University\s+of\s+Science\s+and\s+Technology\s+of\s+China", re.IGNORECASE),
    re.compile(r"USTC", re.IGNORECASE),
    re.compile(r"中国科学技术大学", re.IGNORECASE),
    re.compile(r"中科大", re.IGNORECASE),
]

EXCLUSION_PATTERNS = [
    re.compile(r"Huazhong", re.IGNORECASE),
    re.compile(r"HUST", re.IGNORECASE),
    re.compile(r"华中科技大学", re.IGNORECASE),
    re.compile(r"华中理工", re.IGNORECASE),
]


def matches_target_affiliation(affiliation_text: str) -> bool:
    if not affiliation_text:
        return False
    for p in EXCLUSION_PATTERNS:
        if p.search(affiliation_text):
            return False
    for p in TARGET_AFFILIATION_PATTERNS:
        if p.search(affiliation_text):
            return True
    return False


def filter_by_affiliation(papers: list[dict]) -> list[dict]:
    return [p for p in papers if matches_target_affiliation(p.get("affiliations", ""))]


# ============================================================
# LIS 关键词预过滤（用于宽泛源）
# ============================================================

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


def is_lis_relevant(paper: dict) -> bool:
    text = paper.get("title", "") + " " + paper.get("abstract", "")
    return bool(LIS_KEYWORDS.search(text))


# ============================================================
# RSS 抓取器
# ============================================================

def _extract_affiliations(entry) -> str:
    for field in ("arxiv_affiliation", "author_affiliation", "dc_creator"):
        value = getattr(entry, field, None)
        if value:
            return str(value)
    summary = getattr(entry, "summary", "") or ""
    description = getattr(entry, "description", "") or ""
    text = summary + " " + description
    m = re.search(r"((?:University|Institute|College|Academy)[^.]*?\.)", text, re.IGNORECASE)
    return m.group(1) if m else ""


async def fetch_rss(
    session: aiohttp.ClientSession,
    source: SourceConfig,
    rate_limiter: RateLimiter,
) -> list[dict]:
    """异步获取 RSS 源并解析为标准格式"""
    xml_text = await _fetch_url(session, source.url, rate_limiter)
    if not xml_text:
        return []

    feed = feedparser.parse(xml_text)
    papers = []
    for entry in feed.entries:
        paper = {
            "title": getattr(entry, "title", "").strip(),
            "abstract": getattr(entry, "summary", "").strip(),
            "date": _parse_date(entry),
            "link": getattr(entry, "link", ""),
            "affiliations": _extract_affiliations(entry),
            "source": source.name,
            "tier": source.tier,
            "field": source.field,
        }
        if paper["title"]:
            papers.append(paper)
    return papers


# ============================================================
# Web 页面抓取器（B类期刊 + C类政策站点）
# ============================================================

async def fetch_web(
    session: aiohttp.ClientSession,
    source: SourceConfig,
    rate_limiter: RateLimiter,
) -> list[dict]:
    """
    从 Web 页面抓取内容。

    根据 source.extra["selectors"] 中的 CSS 选择器解析 HTML。
    """
    html = await _fetch_url(session, source.url, rate_limiter)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    selectors = source.extra.get("selectors", {})
    items = []

    # 尝试按配置的选择器解析
    container_sel = selectors.get("item_list", "") or selectors.get("article_list", "")
    if not container_sel:
        # 没有配置选择器，尝试通用解析
        return _generic_web_parse(soup, source)

    containers = soup.select(container_sel)
    # 选择器未匹配到内容时，回退到通用解析
    if not containers:
        return _generic_web_parse(soup, source)
    for container in containers:
        title = ""
        link = ""
        author = ""
        abstract = ""
        date_str = ""

        title_sel = selectors.get("title", "a")
        title_el = container.select_one(title_sel)
        if title_el:
            title = title_el.get_text(strip=True)
            link = title_el.get("href", "")

        author_sel = selectors.get("author", "")
        if author_sel:
            author_el = container.select_one(author_sel)
            if author_el:
                author = author_el.get_text(strip=True)

        abstract_sel = selectors.get("abstract", "") or selectors.get("summary", "")
        if abstract_sel:
            abstract_el = container.select_one(abstract_sel)
            if abstract_el:
                abstract = abstract_el.get_text(strip=True)

        date_sel = selectors.get("date", "")
        if date_sel:
            date_el = container.select_one(date_sel)
            if date_el:
                date_str = date_el.get_text(strip=True)

        if title:
            # 补全相对链接
            if link and not link.startswith("http"):
                base = f"{urlparse(source.url).scheme}://{urlparse(source.url).netloc}"
                link = base + (link if link.startswith("/") else "/" + link)

            items.append({
                "title": title,
                "abstract": abstract,
                "date": _parse_date_str(date_str),
                "link": link,
                "affiliations": author,
                "source": source.name,
                "tier": source.tier,
                "field": source.field,
            })

    return items


def _generic_web_parse(soup: BeautifulSoup, source: SourceConfig) -> list[dict]:
    """
    通用 Web 页面解析：查找所有包含链接的列表项。
    用于没有配置特定选择器的站点。
    """
    items = []
    # 尝试常见的新闻/通知列表结构
    for container in soup.select("li, .item, .news-item, .list-item, article"):
        link_el = container.find("a")
        if not link_el:
            continue
        title = link_el.get_text(strip=True)
        href = link_el.get("href", "")
        if not title or len(title) < 4:
            continue
        if href and not href.startswith("http"):
            base = f"{urlparse(source.url).scheme}://{urlparse(source.url).netloc}"
            href = base + (href if href.startswith("/") else "/" + href)
        items.append({
            "title": title,
            "abstract": "",
            "date": None,
            "link": href,
            "affiliations": "",
            "source": source.name,
            "tier": source.tier,
            "field": source.field,
        })
    return items


# ============================================================
# 出版商 API 抓取器
# ============================================================

async def fetch_api(
    session: aiohttp.ClientSession,
    source: SourceConfig,
    rate_limiter: RateLimiter,
) -> list[dict]:
    """
    通过出版商 API 获取结构化 metadata。

    支持：
    - CrossRef API：通过 ISSN 获取期刊最新文章（免费，无需 API Key）
    - Elsevier / Springer API：预留，需配置 API Key
    """
    api_type = source.extra.get("api_type", "crossref")

    if api_type == "crossref":
        return await _fetch_crossref(session, source, rate_limiter)

    # Elsevier / Springer API 预留
    elsevier_key = os.getenv("ELSEVIER_API_KEY", "")
    springer_key = os.getenv("SPRINGER_API_KEY", "")
    if api_type == "elsevier" and elsevier_key:
        # TODO: 实现 Elsevier API
        pass
    if api_type == "springer" and springer_key:
        # TODO: 实现 Springer API
        pass

    logger.debug("API 类型 %s 未实现或未配置 Key，跳过: %s", api_type, source.name)
    return []


async def _fetch_crossref(
    session: aiohttp.ClientSession,
    source: SourceConfig,
    rate_limiter: RateLimiter,
) -> list[dict]:
    """
    通过 CrossRef API 获取期刊最新文章。

    CrossRef 免费开放，无需 API Key。
    返回标题、DOI、发表日期、作者列表（无摘要）。
    """
    text = await _fetch_url(session, source.url, rate_limiter)
    if not text:
        return []

    try:
        import json
        data = json.loads(text)
    except json.JSONDecodeError:
        logger.warning("CrossRef JSON 解析失败: %s", source.name)
        return []

    items = []
    for work in data.get("message", {}).get("items", []):
        title_list = work.get("title", [])
        title = title_list[0] if title_list else ""
        if not title:
            continue

        # 提取 DOI 链接
        doi = work.get("DOI", "")
        link = f"https://doi.org/{doi}" if doi else ""

        # 提取日期
        date_parts = work.get("published-print", {}).get("date-parts", [[]])
        if not date_parts or not date_parts[0]:
            date_parts = work.get("published-online", {}).get("date-parts", [[]])
        date_str = None
        if date_parts and date_parts[0]:
            parts = date_parts[0]
            if len(parts) >= 3:
                date_str = f"{parts[0]}-{parts[1]:02d}-{parts[2]:02d}"
            elif len(parts) >= 2:
                date_str = f"{parts[0]}-{parts[1]:02d}-01"
            elif len(parts) >= 1:
                date_str = f"{parts[0]}-01-01"

        # 提取作者
        authors = work.get("author", [])
        author_strs = []
        for a in authors[:3]:
            name_parts = []
            if a.get("given"):
                name_parts.append(a["given"])
            if a.get("family"):
                name_parts.append(a["family"])
            if name_parts:
                author_strs.append(" ".join(name_parts))
        affiliations = "; ".join(author_strs) if author_strs else ""

        # CrossRef 无摘要，abstract 留空
        items.append({
            "title": title.strip(),
            "abstract": "",
            "date": date_str,
            "link": link,
            "affiliations": affiliations,
            "source": source.name,
            "tier": source.tier,
            "field": source.field,
        })

    return items


# ============================================================
# 抓取分发器
# ============================================================

async def fetch_one_source(
    session: aiohttp.ClientSession,
    source: SourceConfig,
    rate_limiter: RateLimiter,
) -> list[dict]:
    """根据 fetch_method 分发到对应的抓取函数"""
    try:
        if source.fetch_method == "rss":
            return await fetch_rss(session, source, rate_limiter)
        elif source.fetch_method == "web":
            return await fetch_web(session, source, rate_limiter)
        elif source.fetch_method == "api":
            return await fetch_api(session, source, rate_limiter)
        else:
            logger.warning("未知抓取方式: %s (%s)", source.fetch_method, source.name)
            return []
    except Exception as e:
        logger.exception("抓取异常 %s: %s", source.name, e)
        return []


# ============================================================
# 聚合入口
# ============================================================

async def fetch_all_async(
    apply_affiliation_filter: bool = True,
) -> tuple[list[dict], list[dict]]:
    """
    异步并发抓取所有信源。

    Returns:
        (papers, news) 二元组
    """
    delay_min = float(os.getenv("REQUEST_DELAY_MIN", "3"))
    delay_max = float(os.getenv("REQUEST_DELAY_MAX", "8"))
    rate_limiter = RateLimiter(min_delay=delay_min, max_delay=delay_max)

    paper_sources = get_paper_sources()
    news_sources = get_news_sources()
    all_sources_list = paper_sources + news_sources

    logger.info("启动异步抓取，共 %d 个源", len(all_sources_list))
    logger.info("限流: 同域名间隔 %.1f-%.1fs，最大重试 %d 次", delay_min, delay_max, MAX_RETRIES)

    connector = aiohttp.TCPConnector(limit=10, force_close=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [
            fetch_one_source(session, src, rate_limiter)
            for src in all_sources_list
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # 分离论文和资讯
    papers = []
    news = []
    for src, result in zip(all_sources_list, results):
        if isinstance(result, Exception):
            logger.error("任务异常 %s: %s", src.name, result)
            continue
        if not isinstance(result, list):
            logger.warning("%s 返回非列表结果: %s", src.name, type(result).__name__)
            continue
        for item in result:
            item["content_type"] = src.content_type
            item["tier"] = src.tier
            item["field"] = src.field
            if src.content_type == "paper":
                papers.append(item)
            else:
                news.append(item)

    # 去重
    papers = _deduplicate(papers)
    news = _deduplicate(news)

    # 过滤明显的期刊元数据页或导航条目
    papers = [p for p in papers if not is_noise_item(p)]
    news = [n for n in news if not is_noise_item(n)]

    # 过滤明显无效的资讯（导航链接、过短标题等）
    _NOISE_PHRASES = {
        "sponsors", "contact us", "who we are", "about us",
        "privacy policy", "cookie policy", "terms of use",
        "login", "sign in", "register",
        "subscribe", "newsletter", "menu",
        "archives", "categories", "tags",
    }
    _NOISE_RE = re.compile(r"\b(?:" + "|".join(re.escape(k) for k in _NOISE_PHRASES) + r")\b", re.IGNORECASE)
    news = [
        n for n in news
        if len(n.get("title", "").strip()) >= 8
        and not _NOISE_RE.search(n["title"])
    ]

    # 宽泛源关键词过滤
    papers = [
        p for p in papers
        if p["source"] not in BROAD_SOURCE_NAMES or is_lis_relevant(p)
    ]

    logger.info("共抓取 %d 篇论文，%d 条资讯", len(papers), len(news))

    if apply_affiliation_filter:
        filtered = filter_by_affiliation(papers)
        logger.info("机构过滤后剩余 %d 篇论文", len(filtered))
        papers = filtered

    return papers, news


def _deduplicate(items: list[dict]) -> list[dict]:
    """按标题去重"""
    seen = set()
    result = []
    for item in items:
        key = item.get("title", "").lower().strip()
        if key and key not in seen:
            seen.add(key)
            result.append(item)
    return result


# ============================================================
# 同步包装（供 main.py 调用）
# ============================================================

def fetch_all_papers(apply_affiliation_filter: bool = True) -> list[dict]:
    """同步包装：抓取所有论文"""
    papers, _ = asyncio.run(fetch_all_async(apply_affiliation_filter=apply_affiliation_filter))
    return papers


def fetch_all_news() -> list[dict]:
    """同步包装：抓取所有资讯"""
    _, news = asyncio.run(fetch_all_async(apply_affiliation_filter=False))
    return news


# ============================================================
# Mock 数据（开发/测试用）
# ============================================================

MOCK_PAPERS = [
    {
        "title": "Exploring the Impact of Large Language Models on Academic Literature Review: A Bibliometric Perspective",
        "abstract": "This study investigates the transformative role of Large Language Models (LLMs) in conducting systematic literature reviews within the Library and Information Science domain.",
        "date": "2026-05-08",
        "link": "https://example.com/paper/1",
        "affiliations": "University of Science and Technology of China, Hefei 230026, China",
        "source": "JASIST",
        "tier": "A",
        "field": "information_science",
    },
    {
        "title": "构建面向科研数据管理的本体知识图谱：以大气科学领域为例",
        "abstract": "科研数据的快速增长对数据管理和知识发现提出了新挑战。本研究以大气科学领域为切入点，采用七步法构建了一个领域本体知识图谱。",
        "date": "2026-05-06",
        "link": "https://example.com/paper/2",
        "affiliations": "中国科学技术大学，合肥 230026",
        "source": "中国图书馆学报",
        "tier": "B",
        "field": "knowledge_organization",
    },
    {
        "title": "Altmetrics在人文社科研究成果评价中的适用性研究",
        "abstract": "传统基于引用的评价指标在人文社科领域存在滞后性和覆盖面不足的问题。",
        "date": "2026-05-04",
        "link": "https://example.com/paper/3",
        "affiliations": "University of Science and Technology of China",
        "source": "Scientometrics",
        "tier": "A",
        "field": "bibliometrics",
    },
    {
        "title": "Digital Preservation Strategies for Born-Digital Academic Materials",
        "abstract": "Born-digital academic materials present unique preservation challenges.",
        "date": "2026-05-02",
        "link": "https://example.com/paper/4",
        "affiliations": "USTC, School of Information Management",
        "source": "JASIST",
        "tier": "A",
        "field": "digital_preservation",
    },
]

MOCK_NEWS = [
    {
        "title": "ALA Annual 2026: Key Takeaways for Library Technology Services",
        "abstract": "The American Library Association's annual conference featured major announcements about AI integration in library services.",
        "date": "2026-05-18",
        "link": "https://example.com/news/1",
        "source": "Scholarly Kitchen",
        "tier": "C",
        "field": "library_technology",
    },
    {
        "title": "NISO 发布新版 COUNTER SUSHI 统计标准",
        "abstract": "NISO 宣布 COUNTER Release 5.1 正式发布，新增对开放获取内容的统计支持。",
        "date": "2026-05-17",
        "link": "https://example.com/news/2",
        "source": "NISO News",
        "tier": "C",
        "field": "standards",
    },
]


def fetch_mock_papers() -> list[dict]:
    return [{**p, "content_type": "paper"} for p in MOCK_PAPERS]


def fetch_mock_news() -> list[dict]:
    return [{**n, "content_type": "news", "affiliations": ""} for n in MOCK_NEWS]


if __name__ == "__main__":
    papers, news = asyncio.run(fetch_all_async(apply_affiliation_filter=False))
    print(f"\n论文 ({len(papers)}):")
    for p in papers[:10]:
        print(f"  [{p.get('date')}] [{p.get('source')}] {p['title'][:60]}...")
    print(f"\n资讯 ({len(news)}):")
    for n in news[:10]:
        print(f"  [{n.get('date')}] [{n.get('source')}] {n['title'][:60]}...")
