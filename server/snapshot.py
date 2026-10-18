"""Code-built pitch-deck packs for Tidewell.

Figures are recalculated from the active founder's files. Missing source files are
marked Can't verify — never filled from the example quality bar.
"""

from __future__ import annotations

from server.finance import (
    annual_recurring_revenue,
    compounded_monthly_growth,
    load_income_statement,
    money,
    trailing_gross_margin,
)

DECK_CLAIMS = [
    "$1.37M ARR",
    "Growing 10% month over month",
    "92% gross margin",
    "Monthly logo churn around 1%",
    "Net revenue retention above 110%",
    "$970 CAC, payback under 3 months",
    "$2B TAM",
    "Northern Comfort to 600 seats",
    "$4M → 24 months runway / $5M ARR",
]

PITCH_FILES = [
    "workspace/tidewell-systems/case-index.md",
    "workspace/tidewell-systems/01-overview.md",
    "workspace/tidewell-systems/02-financial-history.md",
    "workspace/tidewell-systems/03-forecast.md",
    "workspace/tidewell-systems/data/README.md",
    "knowledge/audit-checklist.md",
]


def _metrics() -> tuple[dict, dict, dict, dict]:
    rows = load_income_statement()
    arr = annual_recurring_revenue(rows)
    growth_12 = compounded_monthly_growth(rows, "2025-09", "2026-09")
    growth_3 = compounded_monthly_growth(rows, "2026-06", "2026-09")
    margin = trailing_gross_margin(rows, months=12)
    return arr, growth_12, growth_3, margin


def pitch_deck_snapshot() -> dict:
    arr, growth_12, growth_3, margin = _metrics()
    claims = _claim_rows(arr, growth_12, growth_3, margin)
    return {
        "message": _format_snapshot(arr, growth_12, growth_3, margin, claims),
        "calculations": [arr, growth_12, growth_3, margin],
        "claims": claims,
        "topic": "pitch_deck",
        "focus": "snapshot",
        "files": list(PITCH_FILES),
        "offers_deck_draft": True,
    }


def wrong_assumptions() -> dict:
    """Wrong deck assumptions with solutions — no full snapshot table."""
    arr, growth_12, growth_3, margin = _metrics()
    northern_share = (260 * 40) / arr["mrr"]
    message = "\n".join(
        [
            "## Where the deck drifts from the books",
            "",
            "This isn't a scorecard — it's a short list of places the story and the numbers don't line up yet. "
            "That's normal at your stage. For every item below, I'm giving you the exact words to use "
            "(or what to drop) so you don't have to invent the fix under pressure.",
            "",
            f"1. **ARR is $1.37M** → Books: {money(arr['result'])} (MRR × 12). "
            f"Onboarding was mixed in. "
            f"**Say this:** \"{money(arr['result'])} ARR — onboarding is separate.\" *(Historical)*",
            "",
            f"2. **Growing 10% MoM** → {_pct(growth_12['result'])} over 12 months; "
            f"{_pct(growth_3['result'])} last 3. "
            f"**Say this:** \"{_pct(growth_12['result'])} compounded monthly over the year "
            f"({_pct(growth_3['result'])} recently).\" *(Historical)*",
            "",
            f"3. **92% gross margin** → {_pct(margin['reported'])} as booked; "
            f"{_pct(margin['including_customer_success'])} with customer success. "
            f"**Say this:** both numbers; use the fully loaded one for unit economics. *(Historical)*",
            "",
            f"4. **Northern Comfort to 600 seats** → ~{_pct(northern_share)} of MRR at 260 seats; "
            f"600 isn't signed. "
            f"**Say this:** \"260 now; 600 is upside, not the base case.\" *(Historical / founder's claim)*",
            "",
            "5. **$2B TAM** → no source in the files. "
            "**Do this:** remove it, or replace with a sourced bottom-up figure when you have one.",
            "",
            "6. **Churn ~1%, NRR >110%, CAC $970, 24-month runway** → source files not loaded. "
            "**Do this:** drop the precise claims or mark them \"pending\" until the data exists — "
            "you don't need to defend numbers we can't show yet.",
            "",
            "You don't have to rewrite the whole deck tonight. Open **Deck draft** to put these lines on "
            "slides (tagged Victoria until you edit), or say which line to lock first — ARR, growth, or margin.",
        ]
    )
    return {
        "message": message,
        "calculations": [arr, growth_12, growth_3, margin],
        "topic": "pitch_deck",
        "focus": "wrong_assumptions",
        "files": list(PITCH_FILES),
        "offers_deck_draft": True,
    }


def likely_investor_questions() -> dict:
    """Likely questions with short strong answers from calculated figures."""
    arr, growth_12, growth_3, margin = _metrics()
    message = "\n".join(
        [
            "## Likely questions",
            "",
            "Three questions you're likely to get — with a strong answer for each. "
            "Keep it to about a minute out loud.",
            "",
            f"**1. Why isn't ARR $1.37M?**",
            f"- Strong answer: \"ARR is {money(arr['result'])} — September MRR × 12. "
            f"We had {money(arr['onboarding_excluded'])} of one-time onboarding that month; "
            f"that stays out of ARR.\" *(Historical)*",
            "",
            "**2. Are you really growing 10% a month?**",
            f"- Strong answer: \"Compounded monthly growth was {_pct(growth_12['result'])} "
            f"over the last 12 months, and {_pct(growth_3['result'])} from June to September. "
            f"We don't claim a flat 10%.\" *(Historical)*",
            "",
            "**3. Is gross margin really 92%?**",
            f"- Strong answer: \"As booked it's {_pct(margin['reported'])}. "
            f"Including customer success it's {_pct(margin['including_customer_success'])} "
            f"for the last 12 months — that's the number we use for unit economics.\" *(Historical)*",
            "",
            "Which answer do you want to practise saying first?",
        ]
    )
    return {
        "message": message,
        "calculations": [arr, growth_12, growth_3, margin],
        "topic": "pitch_deck",
        "focus": "likely_questions",
        "files": [
            "workspace/tidewell-systems/01-overview.md",
            "workspace/tidewell-systems/data/README.md",
            "knowledge/investor-qa.md",
        ],
    }


def _pct(rate: float) -> str:
    return f"{rate * 100:.1f}%"


def _claim_rows(arr: dict, growth_12: dict, growth_3: dict, margin: dict) -> list[dict]:
    with_onboarding = (arr["mrr"] + arr["onboarding_excluded"]) * 12
    northern_mrr = 260 * 40
    northern_share = northern_mrr / arr["mrr"]
    return [
        {
            "claim": DECK_CLAIMS[0],
            "data": f"{money(arr['result'])} (not {money(with_onboarding)} with onboarding)",
            "status": "Fix",
        },
        {
            "claim": DECK_CLAIMS[1],
            "data": f"{_pct(growth_12['result'])} over 12 months; {_pct(growth_3['result'])} last 3",
            "status": "Reword",
        },
        {
            "claim": DECK_CLAIMS[2],
            "data": (
                f"{_pct(margin['reported'])} as booked; "
                f"{_pct(margin['including_customer_success'])} with customer success"
            ),
            "status": "Fix",
        },
        {
            "claim": DECK_CLAIMS[3],
            "data": "Customer file not loaded",
            "status": "Can't verify",
        },
        {
            "claim": DECK_CLAIMS[4],
            "data": "Cohort file not loaded",
            "status": "Can't verify",
        },
        {
            "claim": DECK_CLAIMS[5],
            "data": "New-customer counts not loaded",
            "status": "Can't verify",
        },
        {
            "claim": DECK_CLAIMS[6],
            "data": "No source in the files",
            "status": "Remove or source",
        },
        {
            "claim": DECK_CLAIMS[7],
            "data": f"~{_pct(northern_share)} of MRR today; 600 seats unsigned",
            "status": "Show as upside",
        },
        {
            "claim": DECK_CLAIMS[8],
            "data": "Cash/forecast CSVs not loaded",
            "status": "Can't verify",
        },
    ]


def _format_snapshot(
    arr: dict,
    growth_12: dict,
    growth_3: dict,
    margin: dict,
    claims: list[dict],
) -> str:
    fix_count = sum(1 for claim in claims if claim["status"] == "Fix")
    northern_mrr = 260 * 40
    northern_share = northern_mrr / arr["mrr"]
    lines = [
        "## Snapshot",
        "",
        (
            f"Good news: the business is real — {money(arr['result'])} ARR from the books. "
            f"A few deck lines need a clean rewrite so you aren't caught out in the room. "
            f"{fix_count} claims to tighten; the rest we reword, mark as upside, or hold until more data lands. "
            f"You don't have to invent the wording — ready-to-use lines are in Solutions below. *(Historical)*"
        ),
        "",
        "## Strengths",
        "",
        f"- Recurring revenue grew {_pct(growth_12['result'])} compounded monthly over the last year. *(Historical)*",
        f"- Gross margin {_pct(margin['reported'])} as booked (hosting, SMS, payments). *(Historical)*",
        "- $278,700 SR&ED received to date — non-dilutive. *(Historical)*",
        "",
        "## What to tighten (not a failure list)",
        "",
        "Take a breath — every early deck has gaps. Naming them here means we can hand you the fix, "
        "not leave you guessing. Scroll to **Solutions** for copy-paste lines for each item.",
        "",
        f"- Deck ARR says $1.37M; books say {money(arr['result'])} (onboarding mixed in).",
        f"- \"10% MoM\" doesn't match {_pct(growth_12['result'])} (12 months) / {_pct(growth_3['result'])} (last 3).",
        f"- \"92% margin\" ignores customer success → {_pct(margin['including_customer_success'])} fully loaded.",
        f"- Northern Comfort ~{_pct(northern_share)} of MRR; 600-seat expansion isn't signed.",
        "- Churn, NRR, CAC, and runway aren't checkable until more files are loaded — we'll park those calmly.",
        "",
        "## Deck claims",
        "",
        "| Claim | Truth | Status |",
        "|---|---|---|",
    ]
    for claim in claims:
        lines.append(f"| {claim['claim']} | {claim['data']} | {claim['status']} |")
    lines.extend(
        [
            "",
            "## Solutions (use these as-is)",
            "",
            "You don't need to craft the answer under stress. Say these out loud or paste them onto the slide — "
            "each one closes a gap above.",
            "",
            (
                f"1. **ARR:** \"{money(arr['result'])} ARR — MRR × 12. "
                f"Onboarding is one-time and separate.\""
            ),
            (
                f"2. **Growth:** \"{_pct(growth_12['result'])} compounded monthly over 12 months "
                f"({_pct(growth_3['result'])} recently).\""
            ),
            (
                f"3. **Margin:** \"{_pct(margin['reported'])} as booked; "
                f"{_pct(margin['including_customer_success'])} with customer success.\""
            ),
            "4. **Northern Comfort:** \"260 seats now; 600 is verbal upside, not signed.\"",
            "5. **TAM:** Remove $2B until you have a sourced bottom-up figure.",
            "6. **Churn / NRR / CAC / runway:** Drop precise claims or mark \"pending\" until the files exist.",
            "",
            "Next: open **Deck draft** — pick a template, I'll place these lines on slides "
            "(tagged Victoria until you edit). I'll ask **Do you want to audit the current draft?** "
            "before a separate reviewer runs `knowledge/audit-checklist.md`. "
            "Or say which line to lock first (ARR, growth, or margin).",
        ]
    )
    return "\n".join(lines)
