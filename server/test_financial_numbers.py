import unittest

from server.agent import respond
from server.finance import export_income_statement, money
from server.financial_numbers import (
    answer_flashcard,
    financial_numbers_intro,
    financial_numbers_lesson,
    parse_flashcard_choice,
)
from server.paths import INCOME_CSV
from server.sessions import Session


class FinancialNumbersTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not INCOME_CSV.exists():
            export_income_statement()

    def test_intro_lists_critical_metrics_before_choice(self):
        pack = financial_numbers_intro()
        self.assertIn("## Numbers investors care about first", pack["message"])
        self.assertIn("**ARR**", pack["message"])
        self.assertIn("**Growth**", pack["message"])
        self.assertIn("flashcards", pack["message"].lower())
        self.assertIn("Which one do you want first?", pack["message"])

    def test_option_two_returns_intro(self):
        chooser = Session(id="chooser", mode="chooser")
        result = respond(chooser, "2")
        self.assertEqual(result["task"], "financial_numbers")
        self.assertIsNone(chooser.numbers_focus)
        self.assertIn("Numbers investors care about first", result["message"])
        self.assertNotIn("flashcard 1", result["message"].lower())

    def test_arr_lesson_opens_flashcard_not_essay(self):
        session = Session(id="s", mode="coaching", task="financial_numbers")
        result = respond(session, "ARR")
        self.assertEqual(session.numbers_focus, "arr")
        self.assertEqual(session.numbers_card, 0)
        self.assertIn(money(1_286_268), result["message"])
        self.assertIn("Flashcard 1 of", result["message"])
        self.assertIn("Reply with **A**, **B**, **C**, or **D**.", result["message"])
        self.assertNotIn("1–4", result["message"])
        self.assertIn("**A)**", result["message"])
        self.assertIn("**B)**", result["message"])
        # Options must stay on separate lines for the chat markdown renderer.
        self.assertRegex(result["message"], r"\*\*A\)\*\*[^\n]+\n\n\*\*B\)\*\*")
        self.assertNotIn("Reply in your own words", result["message"])

    def test_wrong_then_right_advances(self):
        session = Session(id="s", mode="coaching", task="financial_numbers")
        respond(session, "ARR")
        wrong = respond(session, "B")
        self.assertIn("Not quite", wrong["message"])
        self.assertEqual(session.numbers_card, 0)
        self.assertIn("Try again", wrong["message"])
        right = respond(session, "A")
        self.assertIn("Yes", right["message"])
        self.assertEqual(session.numbers_card, 1)
        self.assertIn("Flashcard 2 of", right["message"])

    def test_completing_deck_offers_next_metric(self):
        session = Session(id="s2", mode="coaching", task="financial_numbers")
        respond(session, "ARR")
        respond(session, "A")
        done = respond(session, "B")
        self.assertIn("cleared the **ARR** flashcards", done["message"])
        self.assertIn("Pick another metric", done["message"])
        next_metric = respond(session, "2")
        self.assertEqual(session.numbers_focus, "growth")
        self.assertEqual(session.numbers_card, 0)
        self.assertIn("Flashcard 1 of", next_metric["message"])

    def test_parse_choice(self):
        self.assertEqual(parse_flashcard_choice("A"), 0)
        self.assertEqual(parse_flashcard_choice("b)"), 1)
        self.assertEqual(parse_flashcard_choice("3"), 2)
        self.assertIsNone(parse_flashcard_choice("Growth"))

    def test_growth_lesson_shows_both_windows(self):
        pack = financial_numbers_lesson("growth")
        self.assertIn("12 months", pack["message"])
        self.assertIn("Last 3 months", pack["message"])
        self.assertIn("Flashcard 1 of", pack["message"])

    def test_runway_still_not_invented(self):
        pack = answer_flashcard("runway", 0, "B")
        self.assertEqual(pack["status"], "correct")
        self.assertIn("cannot calculate runway", financial_numbers_lesson("runway")["message"])


if __name__ == "__main__":
    unittest.main()
