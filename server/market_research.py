"""Market research for funding-stage coaching: size, competitors, comparable raises.

Every figure is tagged with a source kind:
  - Public source (web page URL)
  - Founder's claim / plan (case file)
  - Historical (books)
  - Upload (founder upload — not loaded in this demo)
"""

from __future__ import annotations

import re

from server.finance import annual_recurring_revenue, load_income_statement, money
from server.public_resources import citation, resource_by_id
from server.web_fetch import fetch_text
from server.web_search import search_web

# Tidewell context from 01-overview.md (case facts).
INDUSTRY = "field service management software for trades HVAC plumbing"
COMPANY = "Tidewell Dispatch"
FOUNDER_COMPETITORS = ("Jobber", "Housecall Pro", "ServiceTitan")

SEARCHES = {
    "top_down": (
        "field service management software market size North America 2024 2025",
        "FSM software market size CAGR",
    ),
    "competitors": (
        "Jobber Housecall Pro ServiceTitan competitors field service software",
        "best field service management software for small contractors",
    ),
    "raises": (
        "Canadian SaaS seed round size median 2024 2025",
        "Jobber funding round amount",
        "field service software startup seed series A raise",
    ),
}

# Prefer fetching these public-resources.md entries for raise comps.
RAISE_RESOURCE_IDS = (19, 20, 14)  # Carta US, CVCA, Janz $100M paths

_MONEY = re.compile(
    r"\$\s?(\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)\s*"
    r"(billion|million|B|M|bn|mm)?",
    re.IGNORECASE,
)


def market_research_section(*, search: bool = True, fetch_pages: bool = True) -> str:
    """Build the markdown Market research block for option 1."""
    rows = load_income_statement()
    arr = annual_recurring_revenue(rows)
    lines = [
        "## Market research",
        "",
        "Every figure below carries a source tag: "
        "*(Public source: …)*, *(Founder's claim / plan: …)*, *(Historical: …)*, "
        "or *(Upload: not provided)*. "
        "If a page could not be opened, we link it and do **not** invent its numbers.",
        "",
    ]
    lines.extend(_top_down_block(search=search, fetch_pages=fetch_pages))
    lines.append("")
    lines.extend(_bottom_up_block(arr))
    lines.append("")
    lines.extend(_competitors_block(search=search, fetch_pages=fetch_pages))
    lines.append("")
    lines.extend(_raises_block(search=search, fetch_pages=fetch_pages))
    lines.append("")
    lines.append(
        "Next: practise your stage one-liner, dig into one competitor, or tighten the TAM slide."
    )
    return "\n".join(lines)


def _src_public(title: str, url: str) -> str:
    return f"*(Public source: {title} — {url})*"


def _src_founder(file_name: str) -> str:
    return f"*(Founder's claim / plan: `{file_name}`)*"


def _src_hist(file_name: str) -> str:
    return f"*(Historical: `{file_name}`)*"


def _src_upload(label: str) -> str:
    return f"*(Upload: {label} — not provided)*"


def _top_down_block(*, search: bool, fetch_pages: bool) -> list[str]:
    lines = [
        "### Market size — top-down",
        "",
        f"Deck claim: **$2B TAM in North America** — no supporting data in the case files. "
        f"{_src_founder('01-overview.md')}",
        "",
    ]
    hits = _gather_hits(SEARCHES["top_down"], search=search)
    extracted = _extract_from_hits(hits, fetch_pages=fetch_pages, max_pages=3)
    if extracted:
        lines.append("What we could verify from open web pages:")
        lines.append("")
        for item in extracted:
            lines.append(f"- {item['blurb']} {_src_public(item['title'], item['url'])}")
        lines.append("")
        lines.append(
            "Treat these as industry context, not your TAM. Prefer a bottom-up slide you can defend."
        )
    else:
        lines.append(
            "No usable top-down market-size figure in the pages we could open just now. "
            "Do not keep quoting $2B until you have a sourced report or a bottom-up build. "
            f"{_src_upload('market report / TAM model')}"
        )
    return lines


def _bottom_up_block(arr: dict) -> list[str]:
    # Facts from 01-overview.md
    customers = 211
    seats = 2_493
    list_price = 45
    northern_seats = 260
    northern_price = 40
    illustrative_list_arr = seats * list_price * 12
    northern_arr = northern_seats * northern_price * 12
    return [
        "### Market size — bottom-up (from your books and plan)",
        "",
        f"- Active customers: **{customers:,}**; seats: **{seats:,}**; list **${list_price}/seat/month**. "
        f"{_src_hist('01-overview.md')}",
        f"- Books ARR (MRR × 12): **{money(arr['result'])}**. {_src_hist('income statement')}",
        (
            f"- Illustrative if every seat paid list: "
            f"**{seats:,} × ${list_price} × 12 = {money(illustrative_list_arr)}** — "
            f"a capacity check, not a market size. {_src_hist('01-overview.md')}"
        ),
        (
            f"- Largest customer (Northern Comfort): **{northern_seats} seats × ${northern_price}** → "
            f"about **{money(northern_arr)}** annualised seat revenue; 600-seat expansion is **not signed**. "
            f"{_src_founder('01-overview.md')}"
        ),
        (
            "- Raise plan: **$4M seed** aiming toward **$5M ARR** as the next-stage story. "
            f"{_src_founder('01-overview.md')} / {_src_founder('03-forecast.md')}"
        ),
        (
            "- Upload path for a fuller bottom-up TAM (contractors × seats × price × share): "
            f"{_src_upload('TAM workbook or customer universe file')}"
        ),
        "",
        "Investor-ready SOM: start from reachable contractors in your channels × expected seats × price × "
        "realistic win rate — then cite the upload or plan tab that holds the counts.",
    ]


def _competitors_block(*, search: bool, fetch_pages: bool) -> list[str]:
    lines = [
        "### Competitors",
        "",
        (
            "Named by the founders: **Jobber** and **Housecall Pro** (small contractors), "
            f"**ServiceTitan** (larger), plus spreadsheets/paper. {_src_founder('01-overview.md')}"
        ),
        "",
    ]
    hits = _gather_hits(SEARCHES["competitors"], search=search)
    if not hits:
        lines.append(
            "Web search did not return open competitor pages just now. "
            "Keep the founder-named set above; add win/loss notes when you upload them. "
            f"{_src_upload('win/loss or competitive matrix')}"
        )
        return lines
    lines.append("From the web (title + link; open before quoting product claims):")
    lines.append("")
    seen = set()
    for hit in hits[:6]:
        key = hit["url"]
        if key in seen:
            continue
        seen.add(key)
        snippet = hit.get("snippet") or ""
        blurb = snippet[:180] + ("…" if len(snippet) > 180 else "")
        if blurb:
            lines.append(f"- **{hit['title']}** — {blurb} {_src_public(hit['title'], hit['url'])}")
        else:
            lines.append(f"- **{hit['title']}** {_src_public(hit['title'], hit['url'])}")
    if fetch_pages:
        # Confirm at least one page opens; note failures without inventing.
        for hit in hits[:2]:
            page = fetch_text(hit["url"], max_chars=1200)
            if not page.get("ok"):
                lines.append(
                    f"- Could not open {hit['url']} ({page.get('error', 'error')}) — "
                    f"use the link; do not invent its contents."
                )
    lines.append("")
    lines.append(
        f"Case files do not include win/loss reasons. {_src_upload('win/loss tracker')}"
    )
    return lines


def _raises_block(*, search: bool, fetch_pages: bool) -> list[str]:
    lines = [
        "### Comparable raises",
        "",
        (
            f"Your planned raise: **$4M priced seed**. {_src_founder('01-overview.md')} "
            "That is a target, not a closed round."
        ),
        "",
    ]
    # Curated public resources first.
    for rid in RAISE_RESOURCE_IDS:
        item = resource_by_id(rid)
        if not item:
            continue
        page = fetch_text(item["url"], max_chars=2500) if fetch_pages else {"ok": False, "error": "skipped"}
        us_note = " **(US data — label as US if you use it for a Canadian company.)**" if rid == 19 else ""
        if page.get("ok"):
            figures = _money_mentions(page["text"], limit=3)
            if figures:
                lines.append(
                    f"- **{item['title']}** ({item['publisher']}): found on-page mentions "
                    f"{', '.join(figures)}.{us_note} {citation(item)}"
                )
            else:
                lines.append(
                    f"- **{item['title']}** ({item['publisher']}): page opened; no clean $ figure "
                    f"extracted in the snippet — open the report for medians.{us_note} {citation(item)}"
                )
        else:
            lines.append(
                f"- **{item['title']}** ({item['publisher']}): could not fetch "
                f"({page.get('error', 'error')}) — open the link yourself.{us_note} {citation(item)}"
            )

    hits = _gather_hits(SEARCHES["raises"], search=search)
    extracted = _extract_from_hits(hits, fetch_pages=fetch_pages, max_pages=3)
    if extracted:
        lines.append("")
        lines.append("Additional open-web mentions (verify before putting on a slide):")
        lines.append("")
        for item in extracted:
            lines.append(f"- {item['blurb']} {_src_public(item['title'], item['url'])}")
    elif not hits:
        lines.append("")
        lines.append(
            "No extra raise comps from web search this turn. Prefer CVCA/Carta links above "
            f"or an upload of your target-fund comps. {_src_upload('comp raise table')}"
        )
    return lines


def _gather_hits(queries: tuple[str, ...], *, search: bool) -> list[dict]:
    if not search:
        return []
    hits: list[dict] = []
    seen: set[str] = set()
    for query in queries:
        for hit in search_web(query, limit=4):
            if hit["url"] in seen:
                continue
            seen.add(hit["url"])
            hits.append(hit)
    return hits


def _extract_from_hits(
    hits: list[dict], *, fetch_pages: bool, max_pages: int
) -> list[dict]:
    out: list[dict] = []
    if not hits:
        return out
    for hit in hits[: max_pages * 2]:
        if len(out) >= max_pages:
            break
        if fetch_pages:
            page = fetch_text(hit["url"], max_chars=2800)
            if not page.get("ok"):
                continue
            figures = _money_mentions(page["text"], limit=2)
            if not figures:
                continue
            blurb = f"**{hit['title']}**: on-page figures include {', '.join(figures)}"
        else:
            figures = _money_mentions(hit.get("snippet") or "", limit=2)
            if not figures:
                continue
            blurb = f"**{hit['title']}**: snippet mentions {', '.join(figures)}"
        out.append({"title": hit["title"], "url": hit["url"], "blurb": blurb})
    return out


def _money_mentions(text: str, limit: int = 3) -> list[str]:
    found: list[str] = []
    for match in _MONEY.finditer(text or ""):
        amount = match.group(1)
        unit = (match.group(2) or "").strip()
        token = f"${amount}" + (f" {unit}" if unit else "")
        token = re.sub(r"\s+", " ", token)
        if token not in found:
            found.append(token)
        if len(found) >= limit:
            break
    return found
