"""Financial-numbers coaching: flashcards with multiple choice, not free-text essays."""

from __future__ import annotations

import re

from server.finance import (
    annual_recurring_revenue,
    compounded_monthly_growth,
    load_income_statement,
    money,
    trailing_gross_margin,
)

FILES = [
    "workspace/tidewell-systems/case-index.md",
    "workspace/tidewell-systems/01-overview.md",
    "workspace/tidewell-systems/02-financial-history.md",
    "workspace/tidewell-systems/data/README.md",
    "knowledge/glossary.md",
    "workspace/tidewell-systems/glossary-examples.md",
]

METRIC_OPTIONS = [
    {
        "id": "arr",
        "label": "ARR",
        "aliases": ("arr", "annual recurring", "recurring revenue", "mrr"),
        "hints": ("subscription", "onboarding", "how big"),
    },
    {
        "id": "growth",
        "label": "Growth",
        "aliases": ("growth", "growing", "cmgr", "month over month"),
        "hints": ("faster", "slower", "trend"),
    },
    {
        "id": "margin",
        "label": "Gross margin",
        "aliases": ("margin", "gross margin", "cogs"),
        "hints": ("profitability", "support", "customer success"),
    },
    {
        "id": "churn",
        "label": "Churn",
        "aliases": ("churn", "retention", "nrr", "logo churn"),
        "hints": ("cancel", "leave", "stay"),
    },
    {
        "id": "runway",
        "label": "Runway",
        "aliases": ("runway", "burn", "cash"),
        "hints": ("how long", "months left", "run out"),
    },
]

_LETTERS = ("A", "B", "C", "D")
_CHOICE_RE = re.compile(r"^\s*([A-Da-d]|[1-4])(?:[\).:\s].*)?$")


def financial_numbers_intro() -> dict:
    message = "\n".join(
        [
            "## Numbers investors care about first",
            "",
            "In an early seed meeting, these are the figures that usually decide whether the "
            "conversation stays serious:",
            "",
            "1. **ARR** — size of the recurring business (subscription × 12; one-time fees out).",
            "2. **Growth** — whether that ARR is compounding, and whether the recent pace matches the story.",
            "3. **Gross margin** — how much of each revenue dollar is left after delivering the product "
            "(and whether support is in that picture).",
            "4. **Churn / retention** — whether customers stick and expand.",
            "5. **Runway** — months of cash at current burn (needs a cash figure, not only the P&L).",
            "",
            "We can calculate ARR, growth, and margin from your income statement. "
            "Churn and runway need files that are not loaded yet — we can still learn what they mean.",
            "",
            "Pick a metric and I'll walk you through short flashcards (multiple choice). "
            "Wrong answer → short feedback and another try. Right answer → the insight you'd say in a meeting.",
            "",
            "Which one do you want first?",
            "",
        ]
        + [f"{i}. {item['label']}" for i, item in enumerate(METRIC_OPTIONS, start=1)]
    )
    return {
        "message": message,
        "calculations": [],
        "topic": "financial_numbers",
        "files": list(FILES),
    }


def financial_numbers_lesson(metric_id: str, card_index: int = 0) -> dict:
    """Open a metric with a brief, then the flashcard at card_index."""
    ctx = _context()
    cards = _cards(metric_id, ctx)
    if not cards:
        metric_id = "arr"
        cards = _cards(metric_id, ctx)
    index = max(0, min(card_index, len(cards) - 1))
    brief = _brief(metric_id, ctx)
    card_block = _format_card(cards[index], index, len(cards))
    message = "\n".join([brief, "", card_block])
    return {
        "message": message,
        "calculations": _calcs(metric_id, ctx),
        "topic": metric_id,
        "files": list(FILES),
        "metric": metric_id,
        "card_index": index,
        "card_total": len(cards),
    }


def parse_flashcard_choice(text: str) -> int | None:
    """Return 0–3 for A–D / 1–4, else None."""
    match = _CHOICE_RE.match(text.strip())
    if not match:
        return None
    token = match.group(1).upper()
    if token.isdigit():
        return int(token) - 1
    return ord(token) - ord("A")


def answer_flashcard(metric_id: str, card_index: int, text: str) -> dict:
    """
    Grade a flashcard answer.

    Returns keys: status (correct|wrong|invalid|done), message, card_index,
    calculations, topic, files, metric.
    """
    ctx = _context()
    cards = _cards(metric_id, ctx)
    if not cards:
        return {
            "status": "done",
            "message": financial_numbers_intro()["message"],
            "card_index": 0,
            "calculations": [],
            "topic": "financial_numbers",
            "files": list(FILES),
            "metric": metric_id,
        }

    if card_index >= len(cards):
        return {
            "status": "done",
            "message": _done_message(metric_id),
            "card_index": len(cards),
            "calculations": _calcs(metric_id, ctx),
            "topic": metric_id,
            "files": list(FILES),
            "metric": metric_id,
        }

    choice = parse_flashcard_choice(text)
    card = cards[card_index]
    if choice is None or choice >= len(card["options"]):
        return {
            "status": "invalid",
            "message": "\n".join(
                [
                    "Reply with **A**, **B**, **C**, or **D**.",
                    "",
                    _format_card(card, card_index, len(cards)),
                ]
            ),
            "card_index": card_index,
            "calculations": _calcs(metric_id, ctx),
            "topic": metric_id,
            "files": list(FILES),
            "metric": metric_id,
        }

    if choice != card["answer"]:
        picked = card["options"][choice]
        why = card["wrong"].get(choice) or card["wrong"].get("default", "Not quite.")
        return {
            "status": "wrong",
            "message": "\n".join(
                [
                    f"**Not quite.** You picked {_LETTERS[choice]} — {picked}",
                    "",
                    why,
                    "",
                    "Try again — same card:",
                    "",
                    _format_card(card, card_index, len(cards)),
                ]
            ),
            "card_index": card_index,
            "calculations": _calcs(metric_id, ctx),
            "topic": metric_id,
            "files": list(FILES),
            "metric": metric_id,
        }

    insight = card["insight"]
    next_index = card_index + 1
    if next_index >= len(cards):
        return {
            "status": "done",
            "message": "\n".join(
                [
                    f"**Yes — {_LETTERS[choice]}.**",
                    "",
                    insight,
                    "",
                    _done_message(metric_id),
                ]
            ),
            "card_index": next_index,
            "calculations": _calcs(metric_id, ctx),
            "topic": metric_id,
            "files": list(FILES),
            "metric": metric_id,
        }

    next_card = cards[next_index]
    return {
        "status": "correct",
        "message": "\n".join(
            [
                f"**Yes — {_LETTERS[choice]}.**",
                "",
                insight,
                "",
                "Next card:",
                "",
                _format_card(next_card, next_index, len(cards)),
            ]
        ),
        "card_index": next_index,
        "calculations": _calcs(metric_id, ctx),
        "topic": metric_id,
        "files": list(FILES),
        "metric": metric_id,
    }


def _context() -> dict:
    rows = load_income_statement()
    arr = annual_recurring_revenue(rows)
    growth_12 = compounded_monthly_growth(rows, "2025-09", "2026-09")
    growth_3 = compounded_monthly_growth(rows, "2026-06", "2026-09")
    margin = trailing_gross_margin(rows, months=12)
    return {
        "arr": arr,
        "growth_12": growth_12,
        "growth_3": growth_3,
        "margin": margin,
    }


def _calcs(metric_id: str, ctx: dict) -> list:
    return {
        "arr": [ctx["arr"]],
        "growth": [ctx["growth_12"], ctx["growth_3"]],
        "margin": [ctx["margin"]],
        "churn": [],
        "runway": [],
    }.get(metric_id, [ctx["arr"]])


def _pct(rate: float) -> str:
    return f"{rate * 100:.1f}%"


def _format_card(card: dict, index: int, total: int) -> str:
    # Blank lines between options so markdown does not collapse them into one paragraph.
    lines = [
        f"### Flashcard {index + 1} of {total}",
        "",
        card["prompt"],
        "",
    ]
    for i, option in enumerate(card["options"]):
        lines.append(f"**{_LETTERS[i]})** {option}")
        lines.append("")
    lines.append("Reply with **A**, **B**, **C**, or **D**.")
    return "\n".join(lines)


def _done_message(metric_id: str) -> str:
    label = next((m["label"] for m in METRIC_OPTIONS if m["id"] == metric_id), metric_id)
    return "\n".join(
        [
            f"You've cleared the **{label}** flashcards. Nice work — keep those lines for the room.",
            "",
            "Pick another metric when you're ready:",
            "",
        ]
        + [f"{i}. {item['label']}" for i, item in enumerate(METRIC_OPTIONS, start=1)]
    )


def _brief(metric_id: str, ctx: dict) -> str:
    arr = ctx["arr"]
    growth_12 = ctx["growth_12"]
    growth_3 = ctx["growth_3"]
    margin = ctx["margin"]
    with_onboarding = (arr["mrr"] + arr["onboarding_excluded"]) * 12

    if metric_id == "arr":
        return "\n".join(
            [
                "## ARR — flashcards",
                "",
                "**What it measures:** yearly pace of subscription revenue if nothing changed. "
                "Formula: month-end MRR × 12. Onboarding and other one-time fees stay out.",
                "",
                f"**Your books ({arr['period']}):**",
                f"- Subscription (MRR): {money(arr['mrr'])}",
                f"- Onboarding that month: {money(arr['onboarding_excluded'])} *(left out of ARR)*",
                f"- ARR: {money(arr['result'])} *(Historical)*",
                f"- If someone annualised onboarding too: about {money(with_onboarding)} — that is **not** ARR.",
                "",
                "No essays — tap through the cards. I'll hand you the meeting line when you nail each one.",
            ]
        )
    if metric_id == "growth":
        return "\n".join(
            [
                "## Growth — flashcards",
                "",
                "**What it measures:** the steady monthly rate from starting MRR to ending MRR. "
                "Formula: (ending ÷ starting)^(1 ÷ months) − 1. Show a long window and a recent window.",
                "",
                "**Your books:**",
                (
                    f"- 12 months ({growth_12['period']}): "
                    f"{money(growth_12['starting_mrr'])} → {money(growth_12['ending_mrr'])} "
                    f"= {_pct(growth_12['result'])} compounded monthly *(Historical)*"
                ),
                (
                    f"- Last 3 months ({growth_3['period']}): "
                    f"{money(growth_3['starting_mrr'])} → {money(growth_3['ending_mrr'])} "
                    f"= {_pct(growth_3['result'])} compounded monthly *(Historical)*"
                ),
                "",
                "Multiple choice below — wrong picks get a nudge; right picks get the insight.",
            ]
        )
    if metric_id == "margin":
        return "\n".join(
            [
                "## Gross margin — flashcards",
                "",
                "**What it measures:** (revenue − cost of revenue) ÷ revenue. "
                "Your books put hosting, SMS and payment processing in cost of revenue; "
                "customer success salaries sit in operating expenses.",
                "",
                f"**Your books (last 12 months, {margin['period']}):**",
                f"- Revenue: {money(margin['revenue'])}",
                f"- Cost of revenue (as booked): {money(margin['cost_of_revenue'])}",
                f"- Margin as booked: {_pct(margin['reported'])} *(Historical)*",
                f"- Customer success salaries in that window: {money(margin['customer_success_salaries'])}",
                f"- Margin if those salaries sit in cost of revenue: {_pct(margin['including_customer_success'])} *(Historical)*",
                "",
                "Pick letters — I'll hand you the wording when you're right.",
            ]
        )
    if metric_id == "churn":
        return "\n".join(
            [
                "## Churn — flashcards",
                "",
                "**What it measures:** logo churn is customers lost in the month ÷ customers at the start of the month. "
                "Revenue retention (NRR/GRR) needs a cohort of starting MRR and what happened to it.",
                "",
                "**Your files:** customer and MRR-bridge CSVs are not in `data/`, so I cannot calculate churn from the books. "
                "The income statement alone has no customer counts.",
                "",
                f"**Context you do have:** ARR is {money(arr['result'])} on {money(arr['mrr'])} MRR. "
                "Growth can look fine while churn is high if new sales replace leavers — investors separate those stories.",
                "",
                "We'll learn the ideas with cards — no invented churn rate.",
            ]
        )
    # runway
    return "\n".join(
        [
            "## Runway — flashcards",
            "",
            "**What it measures:** months until cash runs out. Formula: cash ÷ monthly net burn. "
            "Net burn is cash spent minus cash from operations (exclude financing). "
            "One-time inflows like SR&ED should be called out separately.",
            "",
            "**Your files:** the loaded income statement has profit/loss, not a cash balance. "
            "Balance-sheet and cash-flow CSVs are not in `data/`, so I cannot calculate runway here. "
            "The overview claims about eight months of cash — treat that as a founder's claim until cash is in the data folder.",
            "",
            f"**Related fact from the P&L:** ARR is {money(arr['result'])}. "
            "Runway answers a different question: how long the company can operate, not how large recurring revenue is.",
            "",
            "Cards next — still no invented runway months.",
        ]
    )


def _cards(metric_id: str, ctx: dict) -> list[dict]:
    arr = ctx["arr"]
    growth_12 = ctx["growth_12"]
    growth_3 = ctx["growth_3"]
    margin = ctx["margin"]
    with_onboarding = (arr["mrr"] + arr["onboarding_excluded"]) * 12

    if metric_id == "arr":
        return [
            {
                "prompt": "What belongs in ARR?",
                "options": [
                    "Only recurring subscription revenue, annualised (MRR × 12)",
                    "Subscription revenue plus one-time onboarding, annualised",
                    "All cash collected this month × 12",
                    "Forecast bookings for next year",
                ],
                "answer": 0,
                "wrong": {
                    1: "Onboarding is one-time. Annualising it inflates ARR — that's how decks drift from the books.",
                    2: "Cash timing ≠ subscription run-rate. ARR is about the recurring pace, not every dollar that hit the bank.",
                    3: "Forecasts are forward-looking. ARR here is historical from the books.",
                    "default": "ARR is MRR × 12 from subscriptions only.",
                },
                "insight": (
                    f"Investors want a clean run-rate. Your books: {money(arr['result'])} ARR "
                    f"({money(arr['mrr'])} MRR × 12). Onboarding {money(arr['onboarding_excluded'])} stays out. "
                    f"Say: \"{money(arr['result'])} ARR — onboarding is separate.\" *(Historical)*"
                ),
            },
            {
                "prompt": f"Your deck says $1.37M ARR. Books show {money(arr['result'])}. What's going on?",
                "options": [
                    "The deck is correct; the books forgot something",
                    "The deck likely mixed onboarding into the annualised figure",
                    "ARR and MRR are the same number with different labels",
                    "You should quote the higher number in the room",
                ],
                "answer": 1,
                "wrong": {
                    0: "We recalculate from the income statement. Prefer the books until a file proves otherwise.",
                    2: "ARR is MRR × 12 — different units, same story. Mixing them confuses people.",
                    3: "Quoting the higher number without the method is how you get caught. Lead with the books.",
                    "default": "Compare deck vs books before you defend either.",
                },
                "insight": (
                    f"If you annualise onboarding too, you get about {money(with_onboarding)} — close to the deck story, "
                    f"but not ARR. Fix the slide to {money(arr['result'])} and say onboarding is one-time. *(Historical)*"
                ),
            },
        ]

    if metric_id == "growth":
        return [
            {
                "prompt": "Looking at your 12-month vs last-3-month compounded rates, what is happening?",
                "options": [
                    f"Speeding up — recent {_pct(growth_3['result'])} beats the year {_pct(growth_12['result'])}",
                    f"Slowing recently — {_pct(growth_3['result'])} is below the 12-month {_pct(growth_12['result'])}",
                    "Both windows are identical, so trend is flat",
                    "You only need the bigger number for investors",
                ],
                "answer": 1,
                "wrong": {
                    0: f"Recent is {_pct(growth_3['result'])}; the year is {_pct(growth_12['result'])}. Recent is lower — that's a slowdown signal.",
                    2: "The two rates differ. Always show both so the trend is honest.",
                    3: "Investors will ask for the recent window. Hiding the slowdown is worse than naming it.",
                    "default": "Compare the two windows side by side.",
                },
                "insight": (
                    f"Recent pace ({_pct(growth_3['result'])}) is softer than the year ({_pct(growth_12['result'])}). "
                    f"Say both out loud so nobody thinks you're only selling the peak. *(Historical)*"
                ),
            },
            {
                "prompt": 'The deck says "10% month over month." What should you do?',
                "options": [
                    "Keep saying 10% — round numbers are fine",
                    f"Replace it with {_pct(growth_12['result'])} over 12 months and {_pct(growth_3['result'])} recently",
                    "Only quote the 3-month rate because it's more current",
                    "Drop growth from the deck entirely",
                ],
                "answer": 1,
                "wrong": {
                    0: "10% doesn't match either calculated window. Rounded marketing lines get challenged.",
                    2: "One window alone can mislead — the year still matters for the longer story.",
                    3: "Growth belongs on the deck; it just needs the real compounded rates.",
                    "default": "Use the calculated windows, not the slogan.",
                },
                "insight": (
                    f"Meeting line: \"{_pct(growth_12['result'])} compounded monthly over the year "
                    f"({_pct(growth_3['result'])} recently).\" *(Historical)*"
                ),
            },
        ]

    if metric_id == "margin":
        return [
            {
                "prompt": "Why might an investor still ask for margin with customer success included?",
                "options": [
                    "Because accountants always put CS in cost of revenue",
                    "To see the fully loaded cost of serving customers, not only hosting/SMS/payments",
                    "Because SR&ED refunds sit in gross margin",
                    "Because ARR already includes support cost",
                ],
                "answer": 1,
                "wrong": {
                    0: "Your books keep CS in operating expenses — that's a policy, not a universal rule.",
                    2: "SR&ED is a cash/tax item, not a gross-margin line.",
                    3: "ARR is revenue run-rate; it doesn't net out support.",
                    "default": "Think about what \"delivering the product\" fully costs.",
                },
                "insight": (
                    f"As booked: {_pct(margin['reported'])}. With customer success in cost of revenue: "
                    f"{_pct(margin['including_customer_success'])}. Give both; use the fully loaded one for unit economics. *(Historical)*"
                ),
            },
            {
                "prompt": 'Deck says 92% gross margin. Which move keeps you safe in the room?',
                "options": [
                    f"Only say {_pct(margin['reported'])} and stop talking",
                    f"Say {_pct(margin['reported'])} as booked, then {_pct(margin['including_customer_success'])} with customer success",
                    f"Only say {_pct(margin['including_customer_success'])} so you look conservative",
                    "Say 92% because it's close enough to the booked figure",
                ],
                "answer": 1,
                "wrong": {
                    0: "Stopping at the booked number invites \"what about support?\" — finish the thought.",
                    2: "Lead with how you book it, then show the fully loaded view so you aren't accused of sandbagging or spinning.",
                    3: "92% is a deck claim; the books are {_pct(margin['reported'])}. Prefer the calculated figure.",
                    "default": "Two numbers beat one slogan.",
                },
                "insight": (
                    f"Script: \"{_pct(margin['reported'])} as booked; {_pct(margin['including_customer_success'])} "
                    f"with customer success.\" *(Historical)*"
                ),
            },
        ]

    if metric_id == "churn":
        return [
            {
                "prompt": 'If the deck says "~1% monthly logo churn," what do you need before you defend it?',
                "options": [
                    "Only the income statement revenue line",
                    "Customer counts (start of month, logos lost) or a retention cohort file",
                    "The ARR figure alone",
                    "A competitor's churn benchmark",
                ],
                "answer": 1,
                "wrong": {
                    0: "P&L revenue has no logo counts — you can't get churn from revenue alone.",
                    2: "ARR size doesn't prove customers stayed.",
                    3: "Benchmarks don't prove your churn. You need your own customer file.",
                    "default": "Logo churn needs customer counts.",
                },
                "insight": (
                    "Until a customer/MRR-bridge file is loaded, drop the precise churn claim or mark it \"pending\". "
                    "You don't need to defend a number we can't show. *(Historical: data not provided)*"
                ),
            },
            {
                "prompt": "Rising ARR with high churn usually means…",
                "options": [
                    "The business is healthier than low-churn growth",
                    "New sales may be replacing leavers — quality of growth is weaker",
                    "Gross margin must be above 90%",
                    "Runway is automatically long",
                ],
                "answer": 1,
                "wrong": {
                    0: "High churn with rising ARR is a leaky bucket — investors discount that growth.",
                    2: "Margin is a separate question from retention.",
                    3: "Runway is about cash and burn, not churn directly.",
                    "default": "Separate growth from retention in your story.",
                },
                "insight": (
                    "Investors split \"we sell a lot\" from \"customers stay.\" "
                    f"You can still say ARR is {money(arr['result'])} while being honest that churn isn't verified yet. *(Historical)*"
                ),
            },
        ]

    if metric_id == "runway":
        return [
            {
                "prompt": "Why can a company with solid ARR still have short runway?",
                "options": [
                    "ARR automatically funds payroll",
                    "Burn can exceed cash collected — runway is cash ÷ net burn, not ARR",
                    "High ARR means investors will always refill cash",
                    "Runway equals months of ARR remaining",
                ],
                "answer": 1,
                "wrong": {
                    0: "ARR is a revenue run-rate, not a cash balance.",
                    2: "Don't assume a raise. Runway is what cash and burn imply today.",
                    3: "Different formulas. Don't mix ARR months with cash runway.",
                    "default": "Runway needs cash and burn.",
                },
                "insight": (
                    f"ARR ({money(arr['result'])}) answers \"how big is recurring revenue?\" "
                    "Runway answers \"how long until cash runs out?\" Different questions. *(Historical)*"
                ),
            },
            {
                "prompt": 'Before promising "24 months runway" on a slide, what must be true?',
                "options": [
                    "You have ARR above $1M",
                    "Cash, net burn, and planned spend are in the data — and one-time items like SR&ED are called out",
                    "The deck already says eight months, so just scale it up",
                    "Gross margin is above 90%",
                ],
                "answer": 1,
                "wrong": {
                    0: "ARR doesn't produce a runway number by itself.",
                    2: "Overview \"~eight months\" is a founder's claim until cash is loaded — don't invent 24.",
                    3: "Margin doesn't equal runway.",
                    "default": "No cash file → no precise runway claim.",
                },
                "insight": (
                    "We can't calculate runway from the P&L alone. Drop \"24 months\" or mark it pending until "
                    "balance-sheet/cash-flow files exist. Exclude financing and call out SR&ED when you do the math. "
                    "*(Historical: data not provided)*"
                ),
            },
        ]

    return []
