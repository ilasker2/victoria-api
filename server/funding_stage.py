"""Code-built funding-stage suggestion for Tidewell.

Uses calculated ARR/growth plus facts from the company overview.
Does not recommend a valuation or advise whether to accept legal terms.
"""

from __future__ import annotations

from server.finance import (
    annual_recurring_revenue,
    compounded_monthly_growth,
    load_income_statement,
    money,
)
from server.market_research import market_research_section
from server.public_resources import citation, resource_by_id

FILES = [
    "workspace/tidewell-systems/case-index.md",
    "workspace/tidewell-systems/01-overview.md",
    "workspace/tidewell-systems/02-financial-history.md",
    "workspace/tidewell-systems/03-forecast.md",
    "knowledge/glossary.md",
    "knowledge/investor-profiles.md",
    "knowledge/public-resources.md",
]


def funding_stage_pack(*, search: bool = True, fetch_pages: bool = True) -> dict:
    rows = load_income_statement()
    arr = annual_recurring_revenue(rows)
    growth_12 = compounded_monthly_growth(rows, "2025-09", "2026-09")
    growth_3 = compounded_monthly_growth(rows, "2026-06", "2026-09")
    message = _format(arr, growth_12, growth_3)
    research = market_research_section(search=search, fetch_pages=fetch_pages)
    message = message + "\n\n" + research
    return {
        "message": message,
        "calculations": [arr, growth_12, growth_3],
        "topic": "funding_stage",
        "files": list(FILES),
    }


def _pct(rate: float) -> str:
    return f"{rate * 100:.1f}%"


def _cite(resource_id: int) -> str:
    item = resource_by_id(resource_id)
    if item is None:
        return ""
    return citation(item)


def _format(arr: dict, growth_12: dict, growth_3: dict) -> str:
    yc_seed = _cite(8)
    pg_raise = _cite(9)
    bdc_vc = _cite(15)
    bdc_angel = _cite(16)
    yc_safe = _cite(17)
    nvca = _cite(18)
    bdc_fund = _cite(22)
    return "\n".join(
        [
            "## Funding stage",
            "",
            (
                f"**Suggestion: priced seed round — matches where you already are.** "
                f"Books show {money(arr['result'])} ARR "
                f"({_pct(growth_12['result'])} compounded monthly over 12 months; "
                f"{_pct(growth_3['result'])} in the last 3). *(Historical)* "
                f"You've already taken pre-seed SAFEs ($1.5M at a $10M cap, then $500K at a $15M cap) "
                f"plus SR&ED cash. Those SAFEs convert at this priced round. *(Historical: `01-overview.md`)* "
                f"Your plan is a **$4M seed** targeting close January 2027 — that's a founder's claim, not a closed deal. "
                f"{yc_seed}"
            ),
            "",
            "In one sentence you can say: "
            f"\"We're a seed-stage SaaS company at {money(arr['result'])} ARR, converting prior SAFEs into a priced round.\"",
            "",
            "## Investors to pursue",
            "",
            "Aligned with your overview, the case archetypes, and Canadian public guides:",
            "",
            f"1. **Lead seed fund (Canadian)** — sets terms, writes the largest cheque, digs into growth and retention. {bdc_vc}",
            f"2. **Angels / operators** — smaller cheques; useful for customer and GTM advice. {bdc_angel}",
            "3. **Strategic (trades / distribution)** — only if the commercial fit is real; watch exclusivity asks.",
            f"4. **Government-backed co-investor** — can sit beside a private lead; usually slower and governance-heavy. {bdc_fund}",
            "",
            "Skip treating a \"skeptical partner\" as a target cheque — they're the internal challenge, not the lead. "
            f"For how seed fundraising usually runs: {pg_raise}",
            "",
            "## Terms to get clear on",
            "",
            "I won't tell you what to accept — a lawyer should review any term sheet. "
            "These four show up often at seed; know what they mean and what to ask. "
            f"Your existing SAFEs follow the YC post-money structure (Canadian form available). {yc_safe} "
            f"For US-style preferred-stock term definitions (Canadian deals use different forms): {nvca}",
            "",
            "**1. Liquidation preference** — On a sale or wind-down, preferred investors often get their money back "
            "(sometimes with a multiple) before common shareholders. "
            "*Ask:* Is it 1× non-participating? Any multiple? Participating or not?",
            "",
            "**2. Pro-rata rights** — Lets an investor buy enough in a later round to keep their ownership %. "
            "*Ask:* Who gets them? Only the lead, or a wide group that could crowd the next round?",
            "",
            "**3. Protective provisions** — Vetoes on major actions (new financing, sale, changing rights). "
            "*Ask:* Which decisions need preferred approval? Can one investor block day-to-day progress?",
            "",
            "**4. Drag-along rights** — If enough shareholders approve a sale, others can be required to sell too. "
            "*Ask:* What vote threshold triggers it? Does it protect a clean exit or hand control to one block?",
            "",
            "*Not legal advice. Have counsel review SAFE conversion and the seed term sheet before you sign.*",
            "",
            "Market research (size, competitors, comparable raises) follows — every figure is sourced.",
        ]
    )
