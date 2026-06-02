"""Tests for the data update pipeline — mocks aiohttp to avoid dependency at import."""

import json
import sys
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock, patch

# Mock heavy / version-sensitive dependencies before importing backend modules
sys.modules["aiohttp"] = MagicMock()
sys.modules["feedparser"] = MagicMock()
sys.modules["bs4"] = MagicMock()

openai_mock = MagicMock()
openai_mock.OpenAI = MagicMock
sys.modules["openai"] = openai_mock

from backend import pipeline


def _existing_item():
    return {
        "id": 1,
        "title": "Existing paper",
        "date": "2026-05-31",
        "link": "https://example.com/existing",
        "source": "JASIST",
        "tier": "A",
        "field": "information_science",
        "content_type": "paper",
        "category": "AI应用",
        "thinking": "测试数据。",
        "scores": {
            "frontier_tech": 8,
            "practical_value": 7,
            "methodological_rigor": 8,
        },
        "one_sentence_summary": "已有条目。",
        "composite_score": 7.7,
        "featured": True,
    }


@dataclass
class PipelineTestConfig:
    output_path: Path
    daily_reports_path: Path
    use_mock: bool = True
    filter_affiliation: bool = False
    llm_model: str = "test-model"
    min_score_avg_paper: float = 6.0
    min_score_avg_news: float = 5.0
    featured_threshold: float = 7.5
    weight_frontier: float = 0.4
    weight_practical: float = 0.35
    weight_rigor: float = 0.25
    max_total_items: int = 500
    app_timezone: str = "Asia/Shanghai"


class PipelineTest(unittest.TestCase):
    def test_skips_daily_report_when_no_items_pass_evaluation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            data_path = root / "data.json"
            reports_path = root / "daily_reports.json"
            data_path.write_text(
                json.dumps([_existing_item()], ensure_ascii=False),
                encoding="utf-8",
            )
            reports_path.write_text(
                json.dumps(
                    [
                        {"date": "2026-05-31", "summary": "keep", "highlights": [], "stats": {}},
                        {"date": "2026-05-30", "summary": "drop", "highlights": [], "stats": {}},
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            cfg = PipelineTestConfig(data_path, reports_path)

            report_mock = patch.object(pipeline, "generate_daily_report").start()
            patch.object(
                pipeline,
                "fetch_mock_papers",
                return_value=[
                    {
                        "title": "New raw paper",
                        "abstract": "",
                        "date": "2026-06-01",
                        "link": "https://example.com/raw",
                        "affiliations": "",
                        "source": "JASIST",
                        "tier": "A",
                        "field": "information_science",
                        "content_type": "paper",
                    }
                ],
            ).start()
            patch.object(pipeline, "fetch_mock_news", return_value=[]).start()
            patch.object(pipeline, "evaluate_papers", return_value=[]).start()
            patch.object(pipeline, "evaluate_news", return_value=[]).start()

            self.assertTrue(pipeline.run_pipeline(cfg))

            self.assertEqual(
                json.loads(data_path.read_text(encoding="utf-8")),
                [_existing_item()],
            )
            self.assertEqual(
                [r["date"] for r in json.loads(reports_path.read_text(encoding="utf-8"))],
                ["2026-05-31"],
            )
            report_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()