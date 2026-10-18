import unittest
from unittest.mock import patch

from server.agent import opening, respond
from server.claude_client import MissingCredentials, complete
from server.finance import export_income_statement, money
from server.materials import read_text
from server.paths import INCOME_CSV
from server.sessions import Session
from server.verify import apply_checks


def session(mode="coaching", profile=None, task=None, numbers_focus=None):
    if task is None and mode == "coaching":
        task = "financial_numbers"
    if task is None and mode == "investor":
        task = "investor_meeting"
    if numbers_focus is None and task == "financial_numbers" and mode == "coaching":
        numbers_focus = "arr"
    return Session(
        id="test-session",
        mode=mode,
        investor_profile=profile,
        task=task,
        numbers_focus=numbers_focus,
    )


class AgentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not INCOME_CSV.exists():
            export_income_statement()

    def test_coaching_arr_comes_from_code(self):
        result = respond(session(), "What is our ARR?")
        self.assertEqual(result["provider"], "local")
        self.assertEqual(result["calculations"][0]["formula"], "subscription_revenue × 12")
        self.assertIn(money(result["calculations"][0]["result"]), result["message"])
        self.assertTrue(result["help_used"])
        self.assertTrue(result["verification"]["ok"])
        self.assertNotIn("tests/conversations", " ".join(result["routed_files"]))

    def test_a_wrong_arr_claim_is_recorded(self):
        result = respond(session(), "Our ARR is $5 million")
        self.assertTrue(any("does not match" in item for item in result["misunderstandings"]))
        self.assertIn("doesn't match", result["message"])

    def test_investor_mode_holds_the_calculation_until_feedback(self):
        practice = session("investor", "the-lead-seed-fund")
        hidden = respond(practice, "Our ARR is $5 million")
        shown = money(practice.last_calculations[0]["result"])
        self.assertTrue(hidden["calculations_withheld"])
        self.assertEqual(hidden["calculations"], [])
        self.assertNotIn(shown, hidden["message"])
        self.assertFalse(hidden["help_used"])
        released = respond(practice, "Please give me feedback")
        self.assertIn(shown, released["message"])
        self.assertEqual(len(released["practice_results"]), 1)
        self.assertFalse(released["practice_results"][0]["help_used"])

    def test_opening_offers_task_menu(self):
        menu = opening(Session(id="chooser", mode="chooser"))
        self.assertIn("Hi, I'm Victoria", menu["message"])
        self.assertIn("Figure out where you are", menu["message"])
        self.assertIn("Learn the financial basics", menu["message"])
        self.assertIn("Review your pitch deck", menu["message"])
        self.assertIn("Practice an investor meeting", menu["message"])
        self.assertIn("Not sure?", menu["message"])
        self.assertEqual(menu["mode"], "chooser")

    def test_task_selection_starts_coaching_focus(self):
        chooser = Session(id="chooser", mode="chooser")
        result = respond(chooser, "2")
        self.assertEqual(result["task"], "financial_numbers")
        self.assertEqual(result["mode"], "coaching")
        self.assertIn("Numbers investors care about first", result["message"])
        self.assertIn("Which one do you want first?", result["message"])
        self.assertIn("flashcards", result["message"].lower())

    def test_option_one_opens_funding_stage_pack(self):
        chooser = Session(id="chooser", mode="chooser")
        result = respond(chooser, "1")
        self.assertEqual(result["task"], "funding_stage")
        self.assertIn("## Funding stage", result["message"])
        self.assertIn("Terms to get clear on", result["message"])

    def test_free_text_guides_to_closest_task(self):
        chooser = Session(id="chooser", mode="chooser")
        result = respond(chooser, "Can you help me understand our financials and metrics?")
        self.assertEqual(result["task"], "financial_numbers")
        self.assertIn("Numbers investors care about first", result["message"])
        self.assertIn("Which one do you want first?", result["message"])

    def test_ambiguous_menu_prompt_asks_to_clarify(self):
        chooser = Session(id="chooser", mode="chooser")
        result = respond(chooser, "I need help with investors and my numbers")
        self.assertIsNone(chooser.task)
        self.assertIn("Did you mean", result["message"])
        self.assertTrue(
            "Understand financial numbers" in result["message"]
            or "Figure out what funding stage you are at" in result["message"]
            or "Simulate investor meeting" in result["message"]
        )

    def test_which_investors_to_pursue_opens_funding_stage(self):
        chooser = Session(id="chooser", mode="chooser")
        result = respond(chooser, "what investors should i pursue")
        self.assertEqual(result["task"], "funding_stage")
        self.assertIn("## Funding stage", result["message"])
        self.assertIn("## Investors to pursue", result["message"])
        self.assertNotIn("surprise me", result["message"])

    def test_pursue_based_on_finances_redirects_from_investor_chooser(self):
        chooser = Session(id="chooser", mode="chooser")
        respond(chooser, "4")
        self.assertEqual(chooser.task, "investor_meeting")
        result = respond(chooser, "i want to know what investor i should pursue based on my finances")
        self.assertEqual(result["task"], "funding_stage")
        self.assertEqual(result["mode"], "coaching")
        self.assertIn("## Investors to pursue", result["message"])
        self.assertNotIn("Playing the", result["message"])

    def test_mid_session_task_switch_to_pitch_deck(self):
        coaching = session(task="financial_numbers")
        result = respond(coaching, "analyze the pitch deck now")
        self.assertEqual(result["task"], "pitch_deck")
        self.assertEqual(result["mode"], "coaching")
        self.assertIsNone(coaching.pitch_focus)
        self.assertIn("Scan for shaky assumptions", result["message"])

    def test_teach_me_from_pitch_opens_financial_flashcards(self):
        coaching = session(task="pitch_deck")
        coaching.pitch_focus = "snapshot"
        result = respond(coaching, "teach me something")
        self.assertEqual(result["task"], "financial_numbers")
        self.assertEqual(result["mode"], "coaching")
        self.assertIsNone(coaching.pitch_focus)
        self.assertIsNone(coaching.numbers_focus)
        self.assertIn("flashcards", result["message"].lower())
        self.assertIn("learning the financial basics", result["message"].lower())

    def test_teach_me_from_funding_stage_opens_financial_flashcards(self):
        coaching = session(task="funding_stage")
        result = respond(coaching, "can you teach me the basics?")
        self.assertEqual(result["task"], "financial_numbers")
        self.assertIsNone(coaching.numbers_focus)
        self.assertIn("multiple choice", result["message"].lower())

    def test_investor_task_asks_for_profile_then_starts(self):
        chooser = Session(id="chooser", mode="chooser")
        menu = respond(chooser, "Simulate investor meeting")
        self.assertEqual(menu["task"], "investor_meeting")
        self.assertEqual(menu["mode"], "chooser")
        self.assertIn("surprise me", menu["message"])
        started = respond(chooser, "2")
        self.assertEqual(started["mode"], "investor")
        self.assertEqual(started["investor_profile"], "the-angel-operator")
        self.assertIn("last customer who churned", started["message"])
        self.assertNotIn("Calculated", started["message"])

    def test_opening_investor_mode_still_works(self):
        investor = opening(session("investor", "the-angel-operator"))
        self.assertIn("last customer who churned", investor["message"])
        self.assertNotIn("Calculated", investor["message"])

    def test_runway_is_not_invented(self):
        practice = session(task="financial_numbers", numbers_focus=None)
        # After intro, picking runway should teach without inventing a figure.
        result = respond(practice, "runway")
        self.assertIn("cannot calculate runway", result["message"])
        self.assertEqual(result["calculations"], [])

    def test_valuation_recommendation_is_replaced(self):
        message, result = apply_checks("I recommend a valuation of $20 million.")
        self.assertFalse(result["ok"])
        self.assertIn("can't recommend a valuation", message)

    def test_claude_valuation_reply_is_revised_before_return(self):
        def fake_complete(system, messages, max_tokens=700):
            return "You should be valued at $20 million."

        with patch("server.claude_client.configured", return_value=True), patch(
            "server.claude_client.complete", fake_complete
        ), patch("server.claude_client.model_name", return_value="test-model"):
            result = respond(session(), "What should our valuation be?")
        self.assertEqual(result["provider"], "claude")
        self.assertIn("can't recommend a valuation", result["message"])
        self.assertNotIn("$20 million", result["message"])
        self.assertTrue(result["verification"]["revised"])

    def test_conversation_example_is_not_a_coaching_input(self):
        with self.assertRaises(FileNotFoundError):
            read_text("tests/conversations/tidewell-example-vicky-output.md")

    def test_missing_key_raises_instead_of_calling(self):
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": ""}, clear=False):
            with self.assertRaises(MissingCredentials):
                complete("system", [{"role": "user", "content": "ping"}])


if __name__ == "__main__":
    unittest.main()
