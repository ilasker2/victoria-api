"""Pitch deck draft builder: templates + Victoria-authored slide copy from solutions."""

from __future__ import annotations

from server.finance import (
    annual_recurring_revenue,
    compounded_monthly_growth,
    load_income_statement,
    money,
    trailing_gross_margin,
)

TEMPLATES = [
    {
        "id": "seed_fix",
        "label": "Seed metrics fix",
        "blurb": "Short deck: the claims that need tightening, with Victoria's ready lines.",
    },
    {
        "id": "yc_seed",
        "label": "YC-style seed",
        "blurb": "Problem → solution → traction → market → ask. Traction slides use your books.",
    },
    {
        "id": "sequoia_outline",
        "label": "Sequoia outline",
        "blurb": "Broader narrative scaffold; numbers still come from solutions + books.",
    },
]


def _pct(rate: float) -> str:
    return f"{rate * 100:.1f}%"


def _metrics() -> tuple[dict, dict, dict, dict]:
    rows = load_income_statement()
    arr = annual_recurring_revenue(rows)
    growth_12 = compounded_monthly_growth(rows, "2025-09", "2026-09")
    growth_3 = compounded_monthly_growth(rows, "2026-06", "2026-09")
    margin = trailing_gross_margin(rows, months=12)
    return arr, growth_12, growth_3, margin


def _slide(
    slide_id: str,
    title: str,
    body: str,
    *,
    solution_key: str | None = None,
) -> dict:
    return {
        "id": slide_id,
        "title": title,
        "body": body,
        "author": "victoria",
        "victoria_body": body,
        "solution_key": solution_key,
    }


def _solution_slides(arr: dict, growth_12: dict, growth_3: dict, margin: dict) -> list[dict]:
    return [
        _slide(
            "arr",
            "Traction — ARR",
            f"{money(arr['result'])} ARR — MRR × 12.\nOnboarding is one-time and separate.",
            solution_key="arr",
        ),
        _slide(
            "growth",
            "Traction — Growth",
            (
                f"{_pct(growth_12['result'])} compounded monthly over 12 months "
                f"({_pct(growth_3['result'])} recently)."
            ),
            solution_key="growth",
        ),
        _slide(
            "margin",
            "Unit economics — Margin",
            (
                f"{_pct(margin['reported'])} gross margin as booked; "
                f"{_pct(margin['including_customer_success'])} with customer success."
            ),
            solution_key="margin",
        ),
        _slide(
            "northern",
            "Logo — Northern Comfort",
            "260 seats now; 600 is verbal upside, not signed.",
            solution_key="northern",
        ),
        _slide(
            "tam",
            "Market",
            "Remove the $2B TAM claim until we have a sourced bottom-up figure.",
            solution_key="tam",
        ),
        _slide(
            "pending",
            "Hold for data",
            "Churn, NRR, CAC, and runway: drop precise claims or mark \"pending\" until source files exist.",
            solution_key="pending",
        ),
    ]


def _slides_for_template(template_id: str) -> list[dict]:
    arr, growth_12, growth_3, margin = _metrics()
    fixes = _solution_slides(arr, growth_12, growth_3, margin)
    if template_id == "yc_seed":
        return [
            _slide(
                "problem",
                "Problem",
                "Trades businesses with 3–30 techs still run jobs from whiteboards and group chats.",
            ),
            _slide(
                "solution",
                "Solution",
                "Tidewell Dispatch: scheduling, routing, quotes, invoices, and customer texts for field teams.",
            ),
            *fixes[:4],
            fixes[4],  # market/TAM
            _slide(
                "ask",
                "The ask",
                "$4M priced seed (founder's plan) to extend runway toward the next stage — not a closed round.",
            ),
        ]
    if template_id == "sequoia_outline":
        return [
            _slide("purpose", "Purpose", "Scheduling and dispatch software for trades field teams."),
            _slide("problem", "Problem", "SMB trades operators lose hours to messy booking and no-shows."),
            _slide("solution", "Solution", "One system for jobs, techs, quotes, invoices, and customer updates."),
            _slide("why_now", "Why now", "Field service software is mainstream for large players; SMB trades are underserved."),
            *fixes,
            _slide(
                "team",
                "Team",
                "Jennifer (CEO) and Craig (CTO) — engineers who built for a real HVAC shop first.",
            ),
            _slide(
                "ask",
                "Financials & ask",
                f"Books: {money(arr['result'])} ARR. Plan: $4M seed (founder's claim). "
                "Use the traction slides above for numbers that survive diligence.",
            ),
        ]
    # seed_fix default
    return [
        _slide(
            "cover",
            "What we're fixing",
            "Victoria drafted these slides from your books and the deck gaps we just found. "
            "Text marked Victoria stays hers until you edit it.",
        ),
        *fixes,
    ]


def list_templates() -> list[dict]:
    return list(TEMPLATES)


def deck_draft_pack(template_id: str | None = None) -> dict:
    """Structured draft for the UI + a short coach message."""
    chosen = template_id or "seed_fix"
    if chosen not in {t["id"] for t in TEMPLATES}:
        chosen = "seed_fix"
    slides = _slides_for_template(chosen)
    arr, growth_12, growth_3, margin = _metrics()
    template = next(t for t in TEMPLATES if t["id"] == chosen)
    message = "\n".join(
        [
            "## Deck draft",
            "",
            f"Template: **{template['label']}**. "
            "I filled each slide with solution copy from your books. "
            "Anything tagged **Victoria** is my draft — once you edit a slide, it becomes **Yours**.",
            "",
            "Open the draft panel to pick another template or rewrite a slide. "
            "I won't put unsourced $2B TAM or pending churn/CAC back on the deck.",
        ]
    )
    return {
        "message": message,
        "draft": {
            "template_id": chosen,
            "templates": list_templates(),
            "slides": slides,
        },
        "calculations": [arr, growth_12, growth_3, margin],
        "topic": "pitch_deck",
        "focus": "deck_draft",
        "files": [
            "workspace/tidewell-systems/01-overview.md",
            "workspace/tidewell-systems/02-financial-history.md",
        ],
    }
