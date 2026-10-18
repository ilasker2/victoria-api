import unittest

from server.finance import export_income_statement, money
from server.paths import INCOME_CSV
from server.sessions import Session
from server.snapshot import likely_investor_questions, pitch_deck_snapshot, wrong_assumptions
from server.agent import opening, respond


class SnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not INCOME_CSV.exists():
            export_income_statement()

    def test_snapshot_has_required_sections(self):
        pack = pitch_deck_snapshot()
        message = pack["message"]
        for heading in (
            "## Snapshot",
            "## Strengths",
            "## What to tighten (not a failure list)",
            "## Deck claims",
            "## Solutions (use these as-is)",
        ):
            self.assertIn(heading, message)
        self.assertIn("ready-to-use lines", message)
        self.assertNotIn("## Top 3 questions", message)
        self.assertEqual(len(pack["claims"]), 9)

    def test_wrong_assumptions_pack(self):
        pack = wrong_assumptions()
        self.assertIn("## Where the deck drifts from the books", pack["message"])
        self.assertIn("exact words to use", pack["message"])
        self.assertIn("**Say this:**", pack["message"])
        self.assertIn(money(1_286_268), pack["message"])

    def test_likely_questions_include_strong_answers(self):
        pack = likely_investor_questions()
        self.assertIn("## Likely questions", pack["message"])
        self.assertIn("Strong answer:", pack["message"])
        self.assertIn(money(1_286_268), pack["message"])

    def test_option_three_prompts_pitch_menu(self):
        chooser = Session(id="chooser", mode="chooser")
        result = respond(chooser, "3")
        self.assertEqual(result["task"], "pitch_deck")
        self.assertIsNone(chooser.pitch_focus)
        self.assertIsNone(result["pitch_focus"])
        self.assertIn("Snapshot", result["message"])
        self.assertIn("Scan for shaky assumptions", result["message"])
        self.assertIn("Raise the likely investor questions", result["message"])
        self.assertIn("You can do all three in any order", result["message"])
        self.assertNotIn("## Weaknesses", result["message"])

    def test_pitch_focus_snapshot(self):
        session = Session(id="s", mode="coaching", task="pitch_deck")
        result = respond(session, "1")
        self.assertEqual(session.pitch_focus, "snapshot")
        self.assertIn("## Snapshot", result["message"])
        self.assertIn("## Solutions", result["message"])

    def test_pitch_focus_wrong_assumptions(self):
        session = Session(id="s", mode="coaching", task="pitch_deck")
        result = respond(session, "Scan for shaky assumptions")
        self.assertEqual(session.pitch_focus, "wrong_assumptions")
        self.assertIn("## Where the deck drifts from the books", result["message"])

    def test_pitch_focus_likely_questions(self):
        session = Session(id="s", mode="coaching", task="pitch_deck")
        result = respond(session, "3")
        self.assertEqual(session.pitch_focus, "likely_questions")
        self.assertIn("Strong answer:", result["message"])

    def test_opening_pitch_without_focus_shows_menu(self):
        result = opening(Session(id="s", mode="coaching", task="pitch_deck"))
        self.assertIn("Scan for shaky assumptions", result["message"])
        self.assertNotIn("## Solutions", result["message"])

    def test_free_text_guides_to_pitch_focus(self):
        session = Session(id="s", mode="coaching", task="pitch_deck")
        result = respond(session, "show me what's wrong on the deck")
        self.assertEqual(session.pitch_focus, "wrong_assumptions")
        self.assertIn("That sounds like", result["message"])
        self.assertIn("## Where the deck drifts from the books", result["message"])


if __name__ == "__main__":
    unittest.main()
