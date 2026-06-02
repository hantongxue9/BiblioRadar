import unittest

from backend.data_contract import (
    is_noise_title,
    normalize_category,
    validate_item,
    validate_items,
)


class DataContractTest(unittest.TestCase):
    def test_normalize_prefixed_paper_category(self):
        self.assertEqual(
            normalize_category("数字图书馆：数字保存、机构知识库", "paper"),
            "数字图书馆",
        )

    def test_normalize_prefixed_news_category(self):
        self.assertEqual(
            normalize_category("行业动态：图书馆新一轮数字化转型", "news"),
            "行业动态",
        )

    def test_unknown_category_falls_back_to_other(self):
        self.assertEqual(normalize_category("无法归类的新标签", "news"), "其他")

    def test_noise_title_detection(self):
        self.assertTrue(is_noise_title("Issue Information"))
        self.assertTrue(is_noise_title(" Cover   Image "))
        self.assertTrue(is_noise_title("Table of Contents"))
        self.assertTrue(is_noise_title("front matter"))
        self.assertFalse(is_noise_title("AI-assisted citation auditing for journals"))

    def test_empty_title_is_noise(self):
        self.assertTrue(is_noise_title(""))
        self.assertTrue(is_noise_title(None))

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

    def test_validate_missing_field(self):
        self.assertTrue(
            any(
                "missing title" in err
                for err in validate_item({"id": 1, "content_type": "paper"})
            )
        )

    def test_validate_invalid_score_dimension(self):
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
            "scores": {"frontier_tech": 11, "practical_value": 0, "methodological_rigor": 7},
            "one_sentence_summary": "摘要。",
            "composite_score": 8.0,
            "featured": True,
        }
        errors = validate_item(item)
        self.assertTrue(any("frontier_tech" in e for e in errors))
        self.assertTrue(any("practical_value" in e for e in errors))

    def test_validate_invalid_date_fmt(self):
        item = {
            "id": 1,
            "title": "A paper",
            "date": "2026/05/31",
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
            "one_sentence_summary": "摘要。",
            "composite_score": 8.0,
            "featured": True,
        }
        errors = validate_item(item)
        self.assertTrue(any("date" in e for e in errors))

    def test_validate_accepts_credibility_score(self):
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
            "one_sentence_summary": "摘要。",
            "composite_score": 8.0,
            "featured": True,
            "credibility_score": 7.5,
        }
        self.assertEqual(validate_item(item), [])

    def test_validate_rejects_invalid_credibility_score(self):
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
            "one_sentence_summary": "摘要。",
            "composite_score": 8.0,
            "featured": True,
            "credibility_score": 15.0,
        }
        errors = validate_item(item)
        self.assertTrue(any("credibility_score" in e for e in errors))

    def test_validate_items_empty(self):
        self.assertEqual(validate_items([]), [])


if __name__ == "__main__":
    unittest.main()