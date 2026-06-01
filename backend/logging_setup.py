"""
BiblioRadar 结构化日志配置。

使用 Python 标准 logging 模块替代 print()，支持时区感知。
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def setup_logging(level: int = logging.INFO,
                  tz: str = "Asia/Shanghai") -> logging.Logger:
    """配置并返回根 logger。"""

    class _TZFormatter(logging.Formatter):
        def formatTime(self, record, datefmt=None):
            dt = datetime.fromtimestamp(record.created, tz=timezone.utc)
            dt = dt.astimezone(ZoneInfo(tz))
            return dt.strftime(datefmt or "%Y-%m-%d %H:%M:%S")

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_TZFormatter(
        fmt="%(asctime)s [%(name)s] %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    handler.setLevel(level)

    logger = logging.getLogger("biblioradar")
    logger.setLevel(level)
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False

    return logger