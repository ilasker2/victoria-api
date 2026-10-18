"""Financial calculations. Results come from the data files, not from model text."""

from __future__ import annotations

import csv
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from xml.etree import ElementTree as ET

from server.paths import INCOME_CSV, INCOME_XLSX

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
EXCEL_EPOCH = datetime(1899, 12, 30)


def excel_serial_to_month(value: str) -> str:
    text = value.strip()
    if len(text) >= 7 and text[4] == "-":
        return text[:7]
    day = EXCEL_EPOCH + timedelta(days=float(text))
    return day.strftime("%Y-%m")


def _shared_strings(book: zipfile.ZipFile) -> list[str]:
    root = ET.fromstring(book.read("xl/sharedStrings.xml"))
    strings = []
    for item in root.findall("m:si", NS):
        parts = [
            node.text or ""
            for node in item.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")
        ]
        strings.append("".join(parts))
    return strings


def _cell_text(cell: ET.Element, strings: list[str]) -> str:
    value = cell.find("m:v", NS)
    if value is None or value.text is None:
        return ""
    if cell.attrib.get("t") == "s":
        return strings[int(value.text)]
    return value.text


def read_income_statement_xlsx(path: Path) -> list[dict]:
    with zipfile.ZipFile(path) as book:
        strings = _shared_strings(book)
        sheet = ET.fromstring(book.read("xl/worksheets/sheet1.xml"))
    rows = sheet.findall("m:sheetData/m:row", NS)
    if not rows:
        raise ValueError(f"no rows in {path}")
    header = [_cell_text(cell, strings) for cell in rows[0].findall("m:c", NS)]
    parsed = []
    for row in rows[1:]:
        values = [_cell_text(cell, strings) for cell in row.findall("m:c", NS)]
        if len(values) != len(header):
            raise ValueError("income statement row does not match the header")
        item = {}
        for key, raw in zip(header, values):
            if key == "month":
                item[key] = excel_serial_to_month(raw)
            else:
                item[key] = float(raw)
        parsed.append(item)
    return parsed


def write_income_statement_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        raise ValueError("refusing to write an empty income statement")
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_income_statement(path: Path = INCOME_CSV) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(
            f"{path} is missing. Run python3 -m server.finance to export it from the original workbook."
        )
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        rows = []
        for raw in reader:
            item = {}
            for key, value in raw.items():
                if key == "month":
                    item[key] = excel_serial_to_month(value)
                else:
                    item[key] = float(value)
            rows.append(item)
    return rows


def export_income_statement(xlsx_path: Path = INCOME_XLSX, csv_path: Path = INCOME_CSV) -> int:
    """Write the derived CSV. Does not modify the workbook."""
    before = xlsx_path.read_bytes()
    rows = read_income_statement_xlsx(xlsx_path)
    write_income_statement_csv(rows, csv_path)
    if xlsx_path.read_bytes() != before:
        raise RuntimeError("export changed the original workbook")
    return len(rows)


def money(value: float) -> str:
    if float(value).is_integer():
        return f"${value:,.0f}"
    return f"${value:,.2f}"


def annual_recurring_revenue(rows: list[dict], month: str | None = None) -> dict:
    """ARR is month-end subscription revenue times 12. Onboarding is excluded."""
    if not rows:
        raise ValueError("income statement is empty")
    if month is None:
        chosen = rows[-1]
    else:
        matches = [row for row in rows if row["month"] == month]
        if not matches:
            known = ", ".join(row["month"] for row in rows)
            raise ValueError(f"no income-statement row for {month}. Available months: {known}")
        chosen = matches[-1]
    if "subscription_revenue" not in chosen:
        raise ValueError("subscription_revenue is not in the income statement")
    mrr = chosen["subscription_revenue"]
    onboarding = chosen.get("onboarding_services_revenue", 0.0)
    return {
        "metric": "ARR",
        "formula": "subscription_revenue × 12",
        "period": chosen["month"],
        "mrr": mrr,
        "onboarding_excluded": onboarding,
        "result": mrr * 12,
        "label": "historical",
        "source": "workspace/tidewell-systems/data/01_income_statement_monthly_actuals.csv",
        "notes": "Onboarding revenue is excluded. ARR is not profit and it is not cash.",
    }


def format_arr(calc: dict) -> str:
    return (
        f"ARR for {calc['period']} is {money(calc['result'])}. (Historical)\n\n"
        f"Formula: {calc['formula']}. "
        f"Subscription revenue that month was {money(calc['mrr'])}. "
        f"Onboarding of {money(calc['onboarding_excluded'])} is left out. "
        f"Source: `{calc['source']}`."
    )


SOURCE_INCOME = "workspace/tidewell-systems/data/01_income_statement_monthly_actuals.csv"


def _row_for_month(rows: list[dict], month: str) -> dict:
    matches = [row for row in rows if row["month"] == month]
    if not matches:
        known = ", ".join(row["month"] for row in rows)
        raise ValueError(f"no income-statement row for {month}. Available months: {known}")
    return matches[-1]


def compounded_monthly_growth(rows: list[dict], start_month: str, end_month: str) -> dict:
    """(Ending MRR ÷ Starting MRR)^(1 ÷ months) − 1."""
    start = _row_for_month(rows, start_month)["subscription_revenue"]
    end = _row_for_month(rows, end_month)["subscription_revenue"]
    start_index = next(i for i, row in enumerate(rows) if row["month"] == start_month)
    end_index = next(i for i, row in enumerate(rows) if row["month"] == end_month)
    months = end_index - start_index
    if months <= 0:
        raise ValueError("end_month must be after start_month")
    if start <= 0:
        raise ValueError("starting MRR must be positive")
    rate = (end / start) ** (1 / months) - 1
    return {
        "metric": "compounded_monthly_growth",
        "formula": "(ending_MRR ÷ starting_MRR)^(1 ÷ months) − 1",
        "period": f"{start_month} to {end_month}",
        "months": months,
        "starting_mrr": start,
        "ending_mrr": end,
        "result": rate,
        "label": "historical",
        "source": SOURCE_INCOME,
    }


def trailing_gross_margin(rows: list[dict], months: int = 12) -> dict:
    """Gross margin on reported COGS, and the version that includes customer success."""
    if len(rows) < months:
        raise ValueError(f"need at least {months} months of income statement")
    window = rows[-months:]
    revenue = sum(row["total_revenue"] for row in window)
    cogs = sum(row["total_cogs"] for row in window)
    customer_success = sum(row["customer_success_salaries"] for row in window)
    if revenue <= 0:
        raise ValueError("revenue must be positive")
    reported = (revenue - cogs) / revenue
    with_support = (revenue - cogs - customer_success) / revenue
    return {
        "metric": "gross_margin",
        "formula": "(revenue − cost of revenue) ÷ revenue",
        "period": f"{window[0]['month']} to {window[-1]['month']}",
        "months": months,
        "revenue": revenue,
        "cost_of_revenue": cogs,
        "customer_success_salaries": customer_success,
        "reported": reported,
        "including_customer_success": with_support,
        "label": "historical",
        "source": SOURCE_INCOME,
        "notes": (
            "Reported cost of revenue is hosting, SMS/telephony and payment processing. "
            "Customer success salaries sit in operating expenses in the books."
        ),
    }


def main() -> None:
    count = export_income_statement()
    print(f"Exported {count} months to {INCOME_CSV}")
    print("Original workbook was not modified.")


if __name__ == "__main__":
    main()
