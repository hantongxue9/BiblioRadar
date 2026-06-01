import unittest

from backend.pipeline_utils import (
    build_report_stats,
    compute_composite_score,
    merge_items,
)


class PipelineUtilsTest(unittest.TestCase):
    def test_compute_paper_composite_score(self):
        item = {
            "content_type": "paper",
            "category": "AI应用",
            "scores": {
                "frontier_tech": 8,
                "practical_value": 6,
                "methodological_rigor": 10,
            },
        }

        result = compute_composite_score(
            item,
            featured_threshold=7.5,
            weight_frontier=0.4,
            weight_practical=0.35,
            weight_rigor=0.25,
        )

        self.assertEqual(result["composite_score"], 7.8)
        self.assertTrue(result["featured"])

    def test_merge_items_preserves_existing_id_and_assigns_new_id(self):
        existing = [
            {
                "id": 5,
                "title": "Existing",
                "date": "2026-05-30",
                "content_type": "paper",
                "category": "AI应用",
            }
        ]
        new_items = [
            {
                "title": "existing",
                "date": "2026-05-31",
                "content_type": "paper",
                "category": "检索与推荐",
            },
            {
                "title": "New item",
                "date": "2026-05-29",
                "content_type": "news",
                "category": "政策标准",
            },
        ]

        merged = merge_items(existing, new_items)

        self.assertEqual(len(merged), 2)
        self.assertEqual(merged[0]["id"], 5)
        self.assertEqual(merged[1]["id"], 6)

    def test_build_report_stats_counts_report_items(self):
        stats = build_report_stats(
            [
                {"content_type": "paper", "featured": True},
                {"content_type": "paper", "featured": False},
                {"content_type": "news", "featured": True},
            ]
        )

        self.assertEqual(stats, {"papers": 2, "news": 1, "featured": 2})


if __name__ == "__main__":
    unittest.main()
