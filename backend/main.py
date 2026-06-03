"""
图情雷达（BiblioRadar）后端 CLI 入口。

调度抓取和评估逻辑，将最终结果写入前端的 public/data.json。
"""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

# 加载项目根目录的 .env
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from .config import Config
from .logging_setup import setup_logging
from .pipeline import run_pipeline

logger = setup_logging()


def main():
    cfg = Config()
    try:
        if not cfg.llm_api_key and not cfg.use_mock:
            logger.warning("LLM_API_KEY 未设置且非 mock 模式，可能导致评估失败")
        run_pipeline(cfg)
    except Exception as exc:
        logger.exception("数据更新失败: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()