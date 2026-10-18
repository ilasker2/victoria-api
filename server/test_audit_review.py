import unittest
from unittest.mock import patch

from server.audit_review import apply_audit_fixes, review_pitch_and_deck
from server.finance import export_income_statement
from server.paths import INCOME_CSV


class AuditReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not INCOME_CSV.exists():
            export_income_statement()

    def test_review_flags_concentration_without_network(self):
        with patch("server.audit_review.search_web", return_value=[]), patch(
            "server.audit_review.fetch_text",
            return_value={"url": "x", "ok": False, "error": "offline"},
        ):
            review = review_pitch_and_deck("seed_fix", search=False)
        self.assertIn("## Audit review", review["message"])
        self.assertIn("knowledge/audit-checklist.md", review["message"])
        self.assertIn("separate reviewer", review["message"].lower())
        self.assertTrue(any(f["status"] == "Fix" for f in review["findings"]))
        self.assertTrue(review["needs_revision"])
        self.assertIn("Suggested fixes", review["prompt"])

    def test_apply_fixes_rewrites_northern_slide(self):
        with patch("server.audit_review.search_web", return_value=[]), patch(
            "server.audit_review.fetch_text",
            return_value={"url": "x", "ok": False, "error": "offline"},
        ):
            pack = apply_audit_fixes("seed_fix", search=False)
        self.assertIn("## Audit fixes applied", pack["message"])
        self.assertTrue(pack.get("audit", {}).get("applied"))
        northern = next(s for s in pack["draft"]["slides"] if s["id"] == "northern")
        self.assertIn("of MRR", northern["body"])
        self.assertEqual(northern["author"], "victoria")

    def test_reaudit_after_apply_does_not_reflag_resolved(self):
        """Live slides are scored after apply; previously applied Fix keys never come back as Fix."""
        with patch("server.audit_review.search_web", return_value=[]), patch(
            "server.audit_review.fetch_text",
            return_value={"url": "x", "ok": False, "error": "offline"},
        ):
            pack = apply_audit_fixes("seed_fix", search=False)
            keys = pack["resolved_keys"]
            self.assertTrue(keys)
            again = review_pitch_and_deck(
                "seed_fix",
                search=False,
                slides=pack["draft"]["slides"],
                resolved_keys=keys,
            )
        fix_keys = {f["key"] for f in again["findings"] if f["status"] == "Fix"}
        self.assertFalse(fix_keys & set(keys), f"circular Fix keys: {fix_keys & set(keys)}")
        # If a check still fires as Fix despite the rewrite, resolved_keys force Cleared.
        with patch("server.audit_review.search_web", return_value=[]), patch(
            "server.audit_review.fetch_text",
            return_value={"url": "x", "ok": False, "error": "offline"},
        ):
            forced = review_pitch_and_deck(
                "seed_fix",
                search=False,
                slides=None,  # fresh template still flags concentration
                resolved_keys=["d_concentration"],
            )
        conc = [f for f in forced["findings"] if f.get("key") == "d_concentration"]
        self.assertTrue(conc)
        self.assertEqual(conc[0]["status"], "Cleared")
        self.assertIn("not re-flagged", forced["founder_line"].lower())


if __name__ == "__main__":
    unittest.main()
