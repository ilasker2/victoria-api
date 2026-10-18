import tempfile
import unittest
from pathlib import Path

from server.finance import (
    annual_recurring_revenue,
    excel_serial_to_month,
    export_income_statement,
    load_income_statement,
    read_income_statement_xlsx,
)
from server.paths import INCOME_CSV, INCOME_XLSX


class FinanceTests(unittest.TestCase):
    def test_excel_epoch_matches_the_workbook_bounds(self):
        self.assertEqual(excel_serial_to_month("45566"), "2024-10")
        self.assertEqual(excel_serial_to_month("46266"), "2026-09")

    def test_arr_excludes_onboarding(self):
        rows = [
            {
                "month": "2026-09",
                "subscription_revenue": 100.0,
                "onboarding_services_revenue": 50.0,
            }
        ]
        result = annual_recurring_revenue(rows)
        self.assertEqual(result["result"], 1200.0)
        self.assertEqual(result["onboarding_excluded"], 50.0)
        self.assertEqual(result["label"], "historical")
        self.assertNotEqual(result["result"], (100 + 50) * 12)

    def test_missing_month_is_an_error(self):
        rows = [{"month": "2026-09", "subscription_revenue": 10.0}]
        with self.assertRaises(ValueError):
            annual_recurring_revenue(rows, month="2020-01")

    def test_export_preserves_the_workbook_and_matches_arr_formula(self):
        before = INCOME_XLSX.read_bytes()
        with tempfile.TemporaryDirectory() as folder:
            csv_path = Path(folder) / "actuals.csv"
            count = export_income_statement(INCOME_XLSX, csv_path)
            self.assertEqual(INCOME_XLSX.read_bytes(), before)
            rows = load_income_statement(csv_path)
        self.assertEqual(count, 24)
        self.assertEqual(rows[0]["month"], "2024-10")
        self.assertEqual(rows[-1]["month"], "2026-09")
        calc = annual_recurring_revenue(rows)
        self.assertEqual(calc["result"], rows[-1]["subscription_revenue"] * 12)
        self.assertEqual(calc["period"], "2026-09")
        direct = read_income_statement_xlsx(INCOME_XLSX)
        self.assertEqual(direct[-1]["subscription_revenue"], rows[-1]["subscription_revenue"])

    def test_checked_in_csv_matches_formula(self):
        if not INCOME_CSV.exists():
            export_income_statement()
        rows = load_income_statement()
        calc = annual_recurring_revenue(rows)
        self.assertEqual(calc["result"], calc["mrr"] * 12)


if __name__ == "__main__":
    unittest.main()
