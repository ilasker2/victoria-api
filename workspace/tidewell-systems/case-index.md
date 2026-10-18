# Case Index: Tidewell Systems

> **Read this file first** for any question about Tidewell's situation, numbers or claims. Then open only the file(s) you need.
> **Role:** Tidewell stands in for a real founder's private data. Treat everything here as one company's facts, never as general benchmarks.

## The company in brief

Tidewell Systems Inc. is a Toronto software company selling scheduling and dispatch software (Tidewell Dispatch) to trades businesses with 3 to 30 field technicians. As of September 30, 2026 it has $1.29M in annual recurring revenue (per the founders' overview), 211 customers, 2,493 seats, 14 staff and about 8 months of cash. The founders, Jennifer (CEO) and Craig (CTO), are strong engineers with no prior experience raising a priced round, building a financial model or managing a P&L.

They plan to raise a $4M seed round closing in January 2027, with investor meetings starting in November 2026. Their worry, in their words: they don't know what a seed investor will ask in the first ten minutes, and they don't want to be caught out on their own numbers.

Currency appears to be CAD (per the MRR chart in Appendix C).

## What each file contains

| File | Source | Contents | Actual or forecast |
|---|---|---|---|
| `01-overview.md` | Appendix A | Company background, product and pricing, team, funding history and SAFE terms, the raise, **the nine claims from the founders' draft deck** | Mixed (facts and founders' claims) |
| `02-financial-history.md` | Appendix B | 24 closed months (Oct 2024 to Sep 2026): quarterly income statement, balance sheet (Sep 2025 and Sep 2026), cash flow, MRR bridge, customers and seats, **bookkeeping policies**, data file list | **Actual** |
| `03-forecast.md` | Appendix C | Founders' 18-month plan (Oct 2026 to Mar 2028): quarterly forecast, operating drivers, **assumptions with the founders' unchecked reasoning**, hiring plan, use of funds | **Forecast** (unverified) |
| `04-investor-qa.md` | Appendix D | 15 likely seed-investor questions with weak and strong answers built on Tidewell's numbers, plus the four-part strong-answer rubric and notes for the agent (no valuation advice, don't invent missing competitor or win/loss data) | Mixed (worked examples drawing on actual and forecast figures) |
| `glossary-examples.md` | Appendix I | Tidewell's figure for each glossary term (ARR, burn multiple, CAC, NRR, runway, and so on), to pair with `knowledge/glossary.md`. Recalculate before quoting. | Mixed (historical figures, plus references to the forecast) |

## Key time periods

- **Historical (actual):** October 2024 to September 2026. Snapshot date is September 30, 2026.
- **Forecast:** October 2026 to March 2028.
- **Fiscal year end:** December 31.
- **Target seed close:** January 2027. **Northern Comfort Group renewal:** March 2027.

## Data files

Only one CSV has been provided so far. Do not assume the others exist, and do not guess their contents.

| File | Referenced in | Status |
|---|---|---|
| `01_income_statement_monthly_actuals.csv` | Appendix B | **Available** (`data/`) |
| `02_balance_sheet_monthly_actuals.csv` | Appendix B | Not provided |
| `03_cash_flow_monthly_actuals.csv` | Appendix B | Not provided |
| `04_mrr_bridge_monthly_actuals.csv` | Appendix B | Not provided |
| `05_customers.csv` | Appendix B | Not provided |
| `06_seats_by_customer_by_month.csv` | Appendix B | Not provided |
| `07_headcount_actuals.csv` | Appendix B | Not provided |
| `08_forecast_18_month_founders_plan.csv` | Appendix C | Not provided |
| `09_forecast_assumptions.csv` | Appendix C | Not provided |
| `10_hiring_plan.csv` | Appendix C | Not provided |

*Update this table whenever a file is added to `data/`.*

## The nine draft deck claims: where to look

The founders built these claims from their own spreadsheet. Some are supported by the data and some are not. The agent should check each one against the data, not accept it. This table only points to where the evidence lives; it does not give verdicts.

| # | Claim | Where to check |
|---|---|---|
| 1 | "$1.37M ARR" | `02` snapshot and MRR bridge (ARR is MRR × 12; compare to September 2026 MRR) |
| 2 | "Growing 10% month over month" | `02` MRR bridge (quarterly); monthly detail needs `04` CSV |
| 3 | "92% gross margin" | `02` income statement; read the bookkeeping policies on what is in cost of revenue |
| 4 | "Monthly logo churn around 1%" | `02` customers and seats table; customer-level detail needs `05` and `06` |
| 5 | "Net revenue retention above 110%" | `02` MRR bridge (expansion, contraction, churn); cohorts need `06` |
| 6 | "$970 CAC, paid back in under 3 months" | `02` sales and marketing expense lines and new customers; note there is no pipeline data |
| 7 | "$2B total addressable market in North America" | **No supporting data in the case files.** Use `knowledge/` guidance on market sizing |
| 8 | "Northern Comfort Group is expanding to 600 seats next year" | `01` (current 260 seats, renews March 2027), `03` assumptions ("Nothing is signed"), `02` deferred revenue note |
| 9 | "$4M gives us 24 months of runway and gets us to $5M ARR" | `03` forecast (ending cash, burn, MRR) and use of funds; `01` for the "Series A at $5M ARR" goal |

## Cautions for the agent

1. **Label every number as actual or forecast.** Appendix B is actual. Appendix C is the founders' plan and has not been checked.
2. **The founders' reasoning is not evidence.** Their quotes in `03-forecast.md` explain their thinking; test them against `02-financial-history.md`.
3. **Bookkeeping policies change how numbers read.** Read the "How the books are kept" section in `02` before computing margins, burn or revenue. Key examples: customer success salaries sit in operating expenses, SR&ED credits are booked when cash arrives, annual plans create deferred revenue, and Northern Comfort Group's prepayment inflates the Q1 2026 cash flow.
4. **Quarterly tables are rounded.** Figures may not add exactly. Use the monthly CSV where possible for precise calculations, and say when you are working from rounded figures.
5. **State what you cannot verify.** If a claim needs data that has not been provided (customer-level files, pipeline data), say so rather than estimating.
6. **Keep the case separate from general knowledge.** Use `knowledge/` for concepts, formulas and investor Q&A criteria. Use this case only for Tidewell's facts.
7. **Reproduce the strong answers in `04-investor-qa.md` from the data; don't copy them.** They cite Tidewell's figures as calculated in Appendix B. Before using any of them, recalculate the number from the files in this folder and state the method. If a figure can't be reproduced (for example, because a customer-level CSV hasn't been provided), say so rather than repeating the example's number.
8. **Don't copy the example output.** `tests/tidewell-example-vicky-output.md` is a hand-written quality bar, not a source of truth. Calculate every figure from the files in this folder, and where the data needed isn't provided, say so instead of repeating the example's number.

## Suggested reading order by task

| Task | Open |
|---|---|
| Orient a new session | This file, then `01-overview.md` |
| Check a deck claim | The row in the claims table above, then the relevant data file |
| Analyze historical performance (burn, margins, growth, churn) | `02-financial-history.md` |
| Stress-test the plan or runway | `03-forecast.md`, then compare to `02` |
| Prepare for investor questions | `01-overview.md` (claims, raise), `knowledge/investor-qa.md`, and whichever of `02` or `03` the question touches |
