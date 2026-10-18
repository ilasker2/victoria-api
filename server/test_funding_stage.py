import unittest
from unittest.mock import patch

from server.agent import respond
from server.finance import export_income_statement, money
from server.funding_stage import funding_stage_pack
from server.paths import INCOME_CSV
from server.sessions import Session


class FundingStageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not INCOME_CSV.exists():
            export_income_statement()

    def test_pack_has_stage_investors_and_terms(self):
        with patch("server.market_research.search_web", return_value=[]), patch(
            "server.market_research.fetch_text",
            return_value={"url": "x", "ok": False, "error": "offline"},
        ):
            pack = funding_stage_pack()
        message = pack["message"]
        self.assertIn("## Funding stage", message)
        self.assertIn("## Investors to pursue", message)
        self.assertIn("## Terms to get clear on", message)
        self.assertIn("## Market research", message)
        self.assertIn("Liquidation preference", message)
        self.assertIn("Pro-rata", message)
        self.assertIn("Protective provisions", message)
        self.assertIn("Drag-along", message)
        self.assertIn("Not legal advice", message)
        self.assertIn(money(1_286_268), message)
        self.assertNotIn("worth $", message.lower())
        self.assertIn("ycombinator.com/library/4A-a-guide-to-seed-fundraising", message)
        self.assertIn("ycombinator.com/safe", message)
        self.assertIn("nvca.org/model-legal-documents", message)
        self.assertIn("knowledge/public-resources.md", pack["files"])

    def test_option_one_returns_pack(self):
        with patch("server.market_research.search_web", return_value=[]), patch(
            "server.market_research.fetch_text",
            return_value={"url": "x", "ok": False, "error": "offline"},
        ):
            chooser = Session(id="chooser", mode="chooser")
            result = respond(chooser, "1")
        self.assertEqual(result["task"], "funding_stage")
        self.assertIn("## Funding stage", result["message"])
        self.assertIn("## Market research", result["message"])
        self.assertIn("Lead seed fund", result["message"])
        self.assertTrue(result["calculations"])


if __name__ == "__main__":
    unittest.main()
