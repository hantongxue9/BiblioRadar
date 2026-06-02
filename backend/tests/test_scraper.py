"""Tests for the scraper — only tests pure functions, no network."""

import sys
import unittest
from unittest.mock import MagicMock

sys.modules["aiohttp"] = MagicMock()
sys.modules["feedparser"] = MagicMock()
sys.modules["bs4"] = MagicMock()

from backend.data_contract import is_noise_item


class ScraperNoiseFilterTest(unittest.TestCase):
    def test_filters_noise_titles(self):
        self.assertTrue(is_noise_item({"title": "Cover Image"}))
        self.assertTrue(is_noise_item({"title": "Issue Information"}))
        self.assertTrue(is_noise_item({"title": "Table of Contents"}))
        self.assertTrue(is_noise_item({"title": ""}))

    def test_passes_legitimate_titles(self):
        self.assertFalse(is_noise_item({"title": "A bibliometric analysis of AI in libraries"}))
        self.assertFalse(is_noise_item({"title": "Open access publishing trends 2026"}))


if __name__ == "__main__":
    unittest.main()