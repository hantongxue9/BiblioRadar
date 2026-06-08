"""
RSS 2.0 feed 生成器。

将 data.json 中的条目转换为标准 RSS feed，供阅读器订阅。
"""

from __future__ import annotations

import logging
from datetime import datetime
from email.utils import format_datetime
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree

logger = logging.getLogger("biblioradar.rss")

_CHANNEL_TITLE = "图情雷达 · BiblioRadar"
_CHANNEL_DESCRIPTION = "图情领域学术追踪 — 每日精选文献与行业资讯"


def generate_feed(items: list, feed_path: Path, site_url: str = "") -> None:
    """根据 data.json 条目生成 RSS 2.0 XML 文件。"""
    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")

    SubElement(channel, "title").text = _CHANNEL_TITLE
    SubElement(channel, "description").text = _CHANNEL_DESCRIPTION
    if site_url:
        SubElement(channel, "link").text = site_url
    SubElement(channel, "language").text = "zh-cn"
    SubElement(channel, "lastBuildDate").text = format_datetime(datetime.utcnow())

    for item in items:
        el = SubElement(channel, "item")
        SubElement(el, "title").text = item.get("title", "")
        SubElement(el, "description").text = item.get("one_sentence_summary", "")
        if item.get("link"):
            SubElement(el, "link").text = item["link"]
            SubElement(el, "guid").text = item["link"]
        if item.get("date"):
            try:
                dt = datetime.strptime(item["date"], "%Y-%m-%d")
                SubElement(el, "pubDate").text = format_datetime(dt)
            except ValueError:
                pass
        if item.get("category"):
            SubElement(el, "category").text = item["category"]

    tree = ElementTree(rss)

    tmp = feed_path.with_suffix(".xml.tmp")
    tree.write(str(tmp), encoding="unicode", xml_declaration=True)
    tmp.replace(feed_path)
    logger.info("RSS feed 已写入 %s（%d 条）", feed_path, len(items))
