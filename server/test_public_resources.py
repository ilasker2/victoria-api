"""Public resource parsing, selection, and citation helpers."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from server.public_resources import (
    load_resources,
    public_bundle,
    resource_by_id,
    resources_for_topic,
)
from server.web_fetch import _html_to_text, fetch_text


class PublicResourcesTests(unittest.TestCase):
    def setUp(self):
        load_resources.cache_clear()

    def test_load_resources_has_seed_and_terms_urls(self):
        items = load_resources()
        by_id = {item["id"]: item for item in items}
        self.assertIn(8, by_id)
        self.assertTrue(by_id[8]["url"].startswith("https://www.ycombinator.com/"))
        self.assertIn(17, by_id)
        self.assertIn("safe", by_id[17]["url"])
        self.assertIn(19, by_id)
        self.assertIn("carta.com", by_id[19]["url"])
        self.assertNotIn("nvca.org", by_id[19]["url"])

    def test_resources_for_funding_stage_includes_seed_and_terms(self):
        ids = {item["id"] for item in resources_for_topic("funding_stage")}
        self.assertTrue({8, 9, 17, 18}.issubset(ids))

    def test_public_bundle_fetches_and_labels_failures(self):
        fake_pages = [
            {
                "url": "https://www.ycombinator.com/library/4A-a-guide-to-seed-fundraising",
                "ok": True,
                "text": "Seed fundraising guide excerpt.",
            },
            {
                "url": "https://paulgraham.com/fr.html",
                "ok": False,
                "error": "HTTP 403",
            },
        ]
        with patch("server.public_resources.fetch_many", return_value=fake_pages):
            bundle = public_bundle("funding_stage", fetch=True, fetch_limit=2)
        self.assertIn("A guide to seed fundraising", bundle)
        self.assertIn("Seed fundraising guide excerpt.", bundle)
        self.assertIn("Could not fetch: HTTP 403", bundle)
        self.assertIn("do not invent", bundle.lower())

    def test_html_to_text_strips_tags(self):
        text = _html_to_text("<html><script>x</script><h1>Title</h1><p>Hello &amp; world</p></html>")
        self.assertIn("Title", text)
        self.assertIn("Hello & world", text)
        self.assertNotIn("<", text)

    def test_fetch_text_reports_http_errors(self):
        with patch("server.web_fetch.urllib.request.urlopen", side_effect=TimeoutError("timed out")):
            result = fetch_text("https://example.com/missing")
        self.assertFalse(result["ok"])
        self.assertIn("timed out", result["error"])

    def test_resource_by_id(self):
        item = resource_by_id(17)
        self.assertIsNotNone(item)
        self.assertEqual(item["publisher"], "Y Combinator")


if __name__ == "__main__":
    unittest.main()
