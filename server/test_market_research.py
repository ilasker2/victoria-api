import unittest
from unittest.mock import patch

from server.finance import export_income_statement, money
from server.funding_stage import funding_stage_pack
from server.market_research import market_research_section
from server.paths import INCOME_CSV


class MarketResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not INCOME_CSV.exists():
            export_income_statement()

    def test_section_has_sourced_blocks_without_network(self):
        with patch("server.market_research.search_web", return_value=[]), patch(
            "server.market_research.fetch_text",
            return_value={"url": "https://example.com", "ok": False, "error": "skipped"},
        ):
            text = market_research_section(search=True, fetch_pages=True)
        self.assertIn("## Market research", text)
        self.assertIn("### Market size — top-down", text)
        self.assertIn("### Market size — bottom-up", text)
        self.assertIn("### Competitors", text)
        self.assertIn("### Comparable raises", text)
        self.assertIn("$2B TAM", text)
        self.assertIn("*(Founder's claim / plan:", text)
        self.assertIn("*(Historical:", text)
        self.assertIn("*(Upload:", text)
        self.assertIn("Jobber", text)
        self.assertIn(money(1_286_268), text)

    def test_top_down_quotes_only_fetched_figures(self):
        hits = [
            {
                "title": "FSM Market Report",
                "url": "https://example.com/fsm",
                "snippet": "Market reaches $5.2 billion",
            }
        ]
        page = {
            "url": "https://example.com/fsm",
            "ok": True,
            "text": "The global FSM software market reaches $5.2 billion by 2027.",
        }
        with patch("server.market_research.search_web", return_value=hits), patch(
            "server.market_research.fetch_text", return_value=page
        ):
            text = market_research_section(search=True, fetch_pages=True)
        self.assertIn("$5.2", text)
        self.assertIn("https://example.com/fsm", text)
        self.assertIn("*(Public source:", text)

    def test_funding_stage_pack_includes_research(self):
        with patch("server.market_research.search_web", return_value=[]), patch(
            "server.market_research.fetch_text",
            return_value={"url": "x", "ok": False, "error": "offline"},
        ):
            pack = funding_stage_pack(search=True, fetch_pages=True)
        self.assertIn("## Market research", pack["message"])
        self.assertIn("## Funding stage", pack["message"])


if __name__ == "__main__":
    unittest.main()
