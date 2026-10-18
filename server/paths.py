"""Project paths. Originals live under source/ and are never written."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE = ROOT / "knowledge"
RULES = ROOT / ".cursor" / "rules"
WORKSPACE = ROOT / "workspace" / "tidewell-systems"
DATA = WORKSPACE / "data"
SOURCE = WORKSPACE / "source"
INCOME_CSV = DATA / "01_income_statement_monthly_actuals.csv"
INCOME_XLSX = SOURCE / "01_income_statement_monthly_actuals.xlsx"
TESTS = ROOT / "tests"

COMPANY_ID = "tidewell-systems"
