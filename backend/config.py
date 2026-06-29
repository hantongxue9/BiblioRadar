"""
BiblioRadar 配置集中管理。

所有可配置项通过环境变量注入，在模块加载时自动读取。
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    """BiblioRadar 全局配置，所有值从环境变量读取并提供默认值。"""

    # ---- LLM ----
    llm_api_key: str = os.environ.get("LLM_API_KEY", "")
    llm_base_url: str = os.environ.get("LLM_BASE_URL", "https://api.deepseek.com")
    llm_model: str = os.environ.get("LLM_MODEL", "mimo-v2.5-pro")

    # ---- 时区 ----
    app_timezone: str = os.environ.get("APP_TIMEZONE", "Asia/Shanghai")

    # ---- 抓取 ----
    use_mock: bool = os.environ.get("USE_MOCK", "false").lower() == "true"
    filter_affiliation: bool = os.environ.get("FILTER_AFFILIATION", "false").lower() == "true"
    request_delay_min: float = float(os.environ.get("REQUEST_DELAY_MIN", "3"))
    request_delay_max: float = float(os.environ.get("REQUEST_DELAY_MAX", "8"))
    max_retries: int = int(os.environ.get("MAX_RETRIES", "3"))
    disable_ssl_verify: bool = os.environ.get("DISABLE_SSL_VERIFY", "false").lower() == "true"

    # ---- 出版商 API Key（可选） ----
    elsevier_api_key: str = os.environ.get("ELSEVIER_API_KEY", "")
    springer_api_key: str = os.environ.get("SPRINGER_API_KEY", "")
    semantic_scholar_api_key: str = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
    openalex_mailto: str = os.environ.get("OPENALEX_MAILTO", "")

    # ---- 评估 ----
    min_score_avg_paper: float = float(os.environ.get("MIN_SCORE_AVG", "6.0"))
    min_score_avg_news: float = float(os.environ.get("MIN_SCORE_AVG_NEWS", "5.0"))

    # ---- 综合分权重 ----
    weight_frontier: float = float(os.environ.get("WEIGHT_FRONTIER", "0.40"))
    weight_practical: float = float(os.environ.get("WEIGHT_PRACTICAL", "0.35"))
    weight_rigor: float = float(os.environ.get("WEIGHT_RIGOR", "0.25"))

    # ---- 精选阈值 ----
    featured_threshold: float = float(os.environ.get("FEATURED_THRESHOLD", "7.5"))

    # ---- 来源控制 ----
    arxiv_score_factor: float = float(os.environ.get("ARXIV_SCORE_FACTOR", "0.85"))

    # ---- 输出 ----
    max_total_items: int = int(os.environ.get("MAX_TOTAL_ITEMS", "500"))
    site_url: str = os.environ.get("SITE_URL", "https://hantongxue9.github.io/BiblioRadar")

    # ---- 路径 ----
    project_root: Path = field(
        default_factory=lambda: Path(__file__).resolve().parent.parent
    )
    output_path: Path = field(init=False)
    daily_reports_path: Path = field(init=False)
    feed_path: Path = field(init=False)
    prompts_dir: Path = field(init=False)

    def __post_init__(self):
        self.output_path = self.project_root / "public" / "data.json"
        self.daily_reports_path = self.output_path.parent / "daily_reports.json"
        self.feed_path = self.output_path.parent / "feed.xml"
        self.prompts_dir = Path(__file__).resolve().parent / "prompts"

        # 出版商 API Key 注入环境变量（保持对其他模块的兼容）
        os.environ.setdefault("ELSEVIER_API_KEY", self.elsevier_api_key)
        os.environ.setdefault("SPRINGER_API_KEY", self.springer_api_key)
        os.environ.setdefault("SEMANTIC_SCHOLAR_API_KEY", self.semantic_scholar_api_key)