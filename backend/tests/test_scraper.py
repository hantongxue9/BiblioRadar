"""Tests for the scraper — only tests pure functions, no network."""

import sys
import unittest
from unittest.mock import MagicMock

sys.modules["aiohttp"] = MagicMock()
sys.modules["feedparser"] = MagicMock()
sys.modules["bs4"] = MagicMock()

from backend.scraper import (
    matches_target_affiliation,
    filter_by_affiliation,
    is_lis_relevant,
    _deduplicate,
    _parse_date_str,
)
from backend.data_contract import is_noise_item


class AffiliationFilterTest(unittest.TestCase):
    def test_matches_ustc(self):
        self.assertTrue(matches_target_affiliation(
            "University of Science and Technology of China"
        ))
        self.assertTrue(matches_target_affiliation(
            "中国科学技术大学, Hefei, China"
        ))
        self.assertTrue(matches_target_affiliation(
            "USTC"
        ))
        self.assertTrue(matches_target_affiliation(
            "中科大"
        ))

    def test_excludes_hust(self):
        self.assertFalse(matches_target_affiliation(
            "Huazhong University of Science and Technology"
        ))
        self.assertFalse(matches_target_affiliation(
            "华中科技大学"
        ))
        self.assertFalse(matches_target_affiliation(
            "HUST"
        ))

    def test_empty_text(self):
        self.assertFalse(matches_target_affiliation(""))
        self.assertFalse(matches_target_affiliation(None))

    def test_filter_by_affiliation(self):
        papers = [
            {"affiliations": "USTC", "title": "A"},
            {"affiliations": "MIT", "title": "B"},
        ]
        self.assertEqual(len(filter_by_affiliation(papers)), 1)


class LisRelevanceTest(unittest.TestCase):
    def test_lis_keyword_match(self):
        self.assertTrue(is_lis_relevant(
            {"title": "A bibliometric analysis of AI in libraries"}
        ))
        self.assertTrue(is_lis_relevant(
            {"title": "Open access publishing trends", "abstract": ""}
        ))
        self.assertTrue(is_lis_relevant(
            {"abstract": "a study on library information retrieval systems"}
        ))

    def test_lis_keyword_no_match(self):
        self.assertFalse(is_lis_relevant(
            {"title": "Quantum computing hardware optimization"}
        ))
        self.assertFalse(is_lis_relevant(
            {"title": "", "abstract": "A study on protein folding."}
        ))


class ParseDateTest(unittest.TestCase):
    def test_parse_iso_date(self):
        self.assertEqual(_parse_date_str("2026-05-31"), "2026-05-31")
        self.assertEqual(_parse_date_str("2026-05-01"), "2026-05-01")

    def test_parse_slashed_date(self):
        self.assertEqual(_parse_date_str("2026/05/31"), "2026-05-31")

    def test_parse_chinese_date(self):
        self.assertEqual(_parse_date_str("2026年5月31日"), "2026-05-31")
        self.assertEqual(_parse_date_str("2026年05月31日"), "2026-05-31")

    def test_parse_invalid_date(self):
        self.assertIsNone(_parse_date_str(""))
        self.assertIsNone(_parse_date_str("not a date"))


class DeduplicateTest(unittest.TestCase):
    def test_deduplicate_by_title(self):
        items = [
            {"title": "Same Title", "source": "A"},
            {"title": "Same Title ", "source": "A"},
            {"title": "Different", "source": "A"},
        ]
        result = _deduplicate(items)
        self.assertEqual(len(result), 2)

    def test_deduplicate_empty(self):
        self.assertEqual(_deduplicate([]), [])


class NoiseFilterTest(unittest.TestCase):
    def test_filters_noise_titles(self):
        self.assertTrue(is_noise_item({"title": "Cover Image"}))
        self.assertTrue(is_noise_item({"title": "Issue Information"}))

    def test_passes_legitimate_titles(self):
        self.assertFalse(is_noise_item({"title": "A bibliometric analysis of AI"}))


if __name__ == "__main__":
    unittest.main()