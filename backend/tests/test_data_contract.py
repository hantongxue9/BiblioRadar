import unittest

from backend.data_contract import (
    is_noise_title,
    normalize_category,
    validate_item,
)


class DataContractTest(unittest.TestCase):
    def test_normalize_prefixed_paper_category(self):
        self.assertEqual(
            normalize_category("数字图书馆：数字保存、机构知识库", "paper"),
            "数字图书馆",
        )

    def test_unknown_category_falls_back_to_other(self):
        self.assertEqual(normalize_category("无法归类的新标签", "news"), "其他")

    def test_noise_title_detection(self):
        self.assertTrue(is_noise_title("Issue Information"))
        self.assertTrue(is_noise_title(" Cover   Image "))
        self.assertFalse(is_noise_title("AI-assisted citation auditing for journals"))

    def test_validate_good_paper_item(self):
        item = {
            "id": 1,
            "title": "A paper",
            "date": "2026-05-31",
            "link": "https://example.com",
            "source": "JASIST",
            "tier": "A",
            "field": "information_science",
            "content_type": "paper",
            "category": "AI应用",
            "scores": {
                "frontier_tech": 8,
                "practical_value": 7,
                "methodological_rigor": 9,
            },
            "one_sentence_summary": "这是一条摘要。",
            "composite_score": 8.0,
            "featured": True,
        }
        self.assertEqual(validate_item(item), [])


if __name__ == "__main__":
    unittest.main()
