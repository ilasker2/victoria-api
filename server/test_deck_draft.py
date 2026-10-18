import unittest

from server.deck_draft import deck_draft_pack, list_templates
from server.finance import export_income_statement, money
from server.paths import INCOME_CSV
from server.snapshot import pitch_deck_snapshot, wrong_assumptions


class DeckDraftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not INCOME_CSV.exists():
            export_income_statement()

    def test_templates_listed(self):
        ids = {t["id"] for t in list_templates()}
        self.assertEqual(ids, {"seed_fix", "yc_seed", "sequoia_outline"})

    def test_draft_slides_are_victoria_authored(self):
        pack = deck_draft_pack("seed_fix")
        self.assertIn("## Deck draft", pack["message"])
        slides = pack["draft"]["slides"]
        self.assertGreaterEqual(len(slides), 5)
        for slide in slides:
            self.assertEqual(slide["author"], "victoria")
            self.assertEqual(slide["body"], slide["victoria_body"])
        bodies = " ".join(s["body"] for s in slides)
        self.assertIn(money(1_286_268), bodies)

    def test_pitch_packs_offer_deck_draft(self):
        self.assertTrue(pitch_deck_snapshot().get("offers_deck_draft"))
        self.assertTrue(wrong_assumptions().get("offers_deck_draft"))


if __name__ == "__main__":
    unittest.main()
