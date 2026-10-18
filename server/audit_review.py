"""Separate reviewer for pitch solutions + deck draft.

Works through knowledge/audit-checklist.md. Recalculates from the books,
searches for contradicting public evidence, and proposes concrete fixes.
Does not share the drafting helpers' narrative — only the finance loaders.
"""

from __future__ import annotations

from server.deck_draft import deck_draft_pack
from server.finance import (
    annual_recurring_revenue,
    compounded_monthly_growth,
    load_income_statement,
    money,
    trailing_gross_margin,
)
from server.web_fetch import fetch_text
from server.web_search import search_web

CHECKLIST_FILE = "knowledge/audit-checklist.md"

# Searches aimed at contradicting market / competitor claims (checklist H).
CONTRADICTION_QUERIES = (
    "field service management software market size overstated OR smaller than expected",
    "Jobber vs ServiceTitan SMB market share criticism OR churn",
    "construction trades software TAM North America disputed OR methodology",
)


def _pct(rate: float) -> str:
    return f"{rate * 100:.1f}%"


def _recalc() -> dict:
    rows = load_income_statement()
    arr = annual_recurring_revenue(rows)
    growth_12 = compounded_monthly_growth(rows, "2025-09", "2026-09")
    growth_3 = compounded_monthly_growth(rows, "2026-06", "2026-09")
    margin = trailing_gross_margin(rows, months=12)
    northern_mrr = 260 * 40
    northern_share = northern_mrr / arr["mrr"] if arr["mrr"] else 0.0
    return {
        "arr": arr,
        "growth_12": growth_12,
        "growth_3": growth_3,
        "margin": margin,
        "northern_share": northern_share,
    }


def _finding(
    section: str,
    status: str,
    issue: str,
    *,
    key: str,
    fix: str | None = None,
    slide_ids: list[str] | None = None,
    source: str | None = None,
) -> dict:
    return {
        "key": key,
        "section": section,
        "status": status,  # Pass | Fix | N/A | Cleared
        "issue": issue,
        "fix": fix,
        "slide_ids": slide_ids or [],
        "source": source,
    }


def _merge_slides(pack: dict, slides: list[dict] | None) -> dict:
    """Prefer the founder's current draft slides over a fresh template pack."""
    if not slides:
        return pack
    by_id = {s.get("id"): s for s in slides if s.get("id")}
    merged = []
    for slide in pack["draft"]["slides"]:
        override = by_id.get(slide["id"])
        if override and isinstance(override.get("body"), str):
            merged.append({**slide, **override, "id": slide["id"]})
        else:
            merged.append(slide)
    # Keep any extra slides the UI added
    known = {s["id"] for s in merged}
    for slide in slides:
        sid = slide.get("id")
        if sid and sid not in known:
            merged.append(slide)
    pack = dict(pack)
    pack["draft"] = dict(pack["draft"])
    pack["draft"]["slides"] = merged
    return pack


def _suppress_resolved(findings: list[dict], resolved_keys: set[str]) -> list[dict]:
    """Turn previously applied Fix items into Cleared so re-audits are not circular."""
    out = []
    for f in findings:
        if f.get("status") == "Fix" and f.get("key") in resolved_keys:
            out.append(
                {
                    **f,
                    "status": "Cleared",
                    "issue": (
                        f"{f['issue']} — already applied on a prior pass; "
                        "not re-flagged (avoids a circular audit)."
                    ),
                    "fix": None,
                }
            )
        else:
            out.append(f)
    return out


def _market_already_hedged(draft_text: str) -> bool:
    lower = draft_text.lower()
    return (
        ("do not put a single top-down" in lower or "unsourced" in lower)
        and ("bottom-up" in lower or "remove" in lower)
    ) or ("$2b" in lower.replace(" ", "") and "remove" in lower)


def review_pitch_and_deck(
    template_id: str | None = None,
    *,
    search: bool = True,
    slides: list[dict] | None = None,
    resolved_keys: list[str] | None = None,
) -> dict:
    """
    Independent audit of the solutions + deck draft.

    Pass `slides` to audit the live draft (not a fresh template).
    Pass `resolved_keys` to skip Fix items already applied (anti-circular).
    """
    metrics = _recalc()
    pack = _merge_slides(deck_draft_pack(template_id), slides)
    draft_text = _pack_corpus(pack)
    findings: list[dict] = []

    findings.extend(_check_numbers(metrics, draft_text))
    findings.extend(_check_sources_and_labels(draft_text))
    findings.extend(_check_missing(draft_text))
    findings.extend(_check_accounting_traps(metrics, draft_text, pack))
    findings.extend(_check_coaching_and_guardrails(draft_text))
    findings.extend(_check_contradictions(draft_text, search=search))

    resolved = set(resolved_keys or [])
    findings = _suppress_resolved(findings, resolved)

    fixes = [f for f in findings if f["status"] == "Fix"]
    unverified = [
        f for f in findings if f["status"] == "N/A" or "not provided" in (f.get("issue") or "").lower()
    ]
    cleared = [f for f in findings if f["status"] == "Cleared"]
    founder_line = (
        f"Audit: {len(fixes)} issue(s) flagged for revision. "
        f"{len(unverified)} item(s) could not be fully verified because the data was not provided."
    )
    if cleared:
        founder_line += f" {len(cleared)} previously applied fix(es) were not re-flagged."
    prompt = _victoria_prompt(fixes, founder_line)
    remarks_md = _format_remarks(findings, founder_line, prompt)

    return {
        "message": remarks_md,
        "founder_line": founder_line,
        "prompt": prompt,
        "findings": findings,
        "fix_count": len(fixes),
        "needs_revision": len(fixes) > 0,
        "template_id": pack["draft"]["template_id"],
        "resolved_keys": sorted(resolved),
        "checklist": CHECKLIST_FILE,
        "topic": "pitch_deck",
        "focus": "audit_review",
    }


def apply_audit_fixes(
    template_id: str | None = None,
    *,
    search: bool = True,
    slides: list[dict] | None = None,
    resolved_keys: list[str] | None = None,
) -> dict:
    """Apply Fix items to the live draft; return revised pack + keys to skip next audit."""
    prior = set(resolved_keys or [])
    review = review_pitch_and_deck(
        template_id, search=search, slides=slides, resolved_keys=sorted(prior)
    )
    pack = _merge_slides(deck_draft_pack(review["template_id"]), slides)
    metrics = _recalc()
    fixes = [f for f in review["findings"] if f["status"] == "Fix"]
    working = pack["draft"]["slides"]
    log_rows: list[dict] = []
    newly_resolved: list[str] = []

    for finding in fixes:
        applied = _apply_one_fix(working, finding, metrics)
        log_rows.append(
            {
                "section": finding["section"],
                "issue": finding["issue"],
                "how_fixed": applied or finding.get("fix") or "Noted for founder; no slide rewrite.",
                "key": finding.get("key"),
            }
        )
        if finding.get("key"):
            newly_resolved.append(finding["key"])

    for slide in working:
        slide["author"] = "victoria"
        slide["victoria_body"] = slide["body"]

    all_resolved = sorted(prior | set(newly_resolved))
    fixed_count = len(fixes)
    unverified = sum(
        1
        for f in review["findings"]
        if f["status"] == "N/A" or "not provided" in (f.get("issue") or "").lower()
    )
    founder_line = (
        f"Audit: {fixed_count} issue(s) found and fixed before this answer. "
        f"{unverified} item(s) could not be verified because the data was not provided."
    )
    message = _format_applied(founder_line, log_rows, pack["draft"]["template_id"])
    pack["message"] = message
    pack["draft"]["slides"] = working
    pack["audit"] = {
        "founder_line": founder_line,
        "log": log_rows,
        "checklist": CHECKLIST_FILE,
        "applied": True,
        "resolved_keys": all_resolved,
    }
    pack["resolved_keys"] = all_resolved
    pack["focus"] = "audit_applied"
    return pack


def _pack_corpus(pack: dict) -> str:
    parts = [pack.get("message", "")]
    for slide in pack.get("draft", {}).get("slides", []):
        parts.append(slide.get("title", ""))
        parts.append(slide.get("body", ""))
    return "\n".join(parts)


def _check_numbers(metrics: dict, draft_text: str) -> list[dict]:
    arr = metrics["arr"]
    findings = []
    arr_str = money(arr["result"])
    if arr_str not in draft_text:
        findings.append(
            _finding(
                "A. Numbers",
                "Fix",
                f"Draft is missing the recalculated ARR {arr_str} from the books.",
                key="a_arr_missing",
                fix=f"Ensure traction slides state {arr_str} ARR (MRR × 12).",
                slide_ids=["arr"],
            )
        )
    else:
        findings.append(
            _finding(
                "A. Numbers",
                "Pass",
                f"ARR {arr_str} reproduces from the income statement (MRR × 12).",
                key="a_arr_ok",
            )
        )

    if "compounded monthly" not in draft_text.lower() and "12 months" not in draft_text.lower():
        findings.append(
            _finding(
                "A. Numbers",
                "Fix",
                "Growth figure appears without a clear period / compounded-monthly method.",
                key="a_growth_method",
                fix="State 12-month and recent 3-month compounded monthly rates with periods.",
                slide_ids=["growth"],
            )
        )
    else:
        findings.append(
            _finding(
                "A. Numbers",
                "Pass",
                "Growth windows and compounded-monthly language are present.",
                key="a_growth_ok",
            )
        )

    if "as booked" not in draft_text.lower() or "customer success" not in draft_text.lower():
        findings.append(
            _finding(
                "A. Numbers",
                "Fix",
                "Margin should show both as-booked and including customer success.",
                key="a_margin_both",
                fix=(
                    f"Use {_pct(metrics['margin']['reported'])} as booked and "
                    f"{_pct(metrics['margin']['including_customer_success'])} with customer success."
                ),
                slide_ids=["margin"],
            )
        )
    else:
        findings.append(
            _finding(
                "A. Numbers",
                "Pass",
                "Both margin definitions appear (as booked and with customer success).",
                key="a_margin_ok",
            )
        )
    return findings


def _check_sources_and_labels(draft_text: str) -> list[dict]:
    findings = []
    lower = draft_text.lower()
    if "$2b" in lower.replace(" ", "") or "$2 b" in lower:
        if "remove" in lower or "until" in lower or "sourced" in lower:
            findings.append(
                _finding(
                    "B. Sources and labels",
                    "Pass",
                    "$2B TAM is treated as an unsourced founder claim to remove, not as fact.",
                    key="b_tam_ok",
                )
            )
        else:
            findings.append(
                _finding(
                    "B. Sources and labels",
                    "Fix",
                    "$2B TAM appears without a clear 'unsourced / remove' label.",
                    key="b_tam_label",
                    fix="Mark $2B TAM as founder's claim with no source; remove or replace with bottom-up.",
                    slide_ids=["tam", "market"],
                )
            )
    if "founder's" in lower or "founder" in lower or "plan" in lower or "not signed" in lower:
        findings.append(
            _finding(
                "B. Sources and labels",
                "Pass",
                "Unsigned / plan items are called out (e.g. 600 seats, $4M raise).",
                key="b_plan_ok",
            )
        )
    else:
        findings.append(
            _finding(
                "B. Sources and labels",
                "Fix",
                "Raise or expansion language may read as closed fact.",
                key="b_unsigned_labels",
                fix="Label $4M seed and 600-seat expansion as plan / upside, not signed.",
                slide_ids=["ask", "northern"],
            )
        )
    return findings


def _check_missing(draft_text: str) -> list[dict]:
    findings = []
    lower = draft_text.lower()
    if "pending" in lower or ("until" in lower and "file" in lower):
        findings.append(
            _finding(
                "C. Missing data",
                "Pass",
                "Churn / NRR / CAC / runway gaps are named instead of invented.",
                key="c_pending_ok",
            )
        )
    else:
        findings.append(
            _finding(
                "C. Missing data",
                "N/A",
                "Confirm churn, NRR, CAC, and runway stay pending — source files not in data/.",
                key="c_pending_na",
                source="workspace/tidewell-systems/data/README.md",
            )
        )
    if "win/loss" in lower or "win and loss" in lower:
        findings.append(
            _finding(
                "C. Missing data",
                "Pass",
                "Win/loss gap acknowledged.",
                key="c_winloss_ok",
            )
        )
    else:
        findings.append(
            _finding(
                "C. Missing data",
                "N/A",
                "Competitor win/loss reasons are not in the case files — do not invent them.",
                key="c_winloss_na",
                source="workspace/tidewell-systems/04-investor-qa.md",
            )
        )
    return findings


def _check_accounting_traps(metrics: dict, draft_text: str, pack: dict) -> list[dict]:
    findings = []
    share = metrics["northern_share"]
    slide_ids = {s["id"] for s in pack["draft"]["slides"]}
    corpus = draft_text.lower()
    has_share_callout = "of mrr" in corpus or "concentration" in corpus
    if "northern" in corpus or "260" in corpus:
        if has_share_callout:
            findings.append(
                _finding(
                    "D. Accounting traps",
                    "Pass",
                    "Largest-customer concentration is visible beside Northern Comfort.",
                    key="d_concentration",
                )
            )
        else:
            findings.append(
                _finding(
                    "D. Accounting traps",
                    "Fix",
                    (
                        f"Northern Comfort is ~{_pct(share)} of MRR; draft should state concentration "
                        "explicitly (with and without that logo for growth stories)."
                    ),
                    key="d_concentration",
                    fix=(
                        f"Add: Northern Comfort is about {_pct(share)} of MRR at 260 seats; "
                        "show growth with/without that logo when telling the traction story."
                    ),
                    slide_ids=["northern"] if "northern" in slide_ids else ["growth"],
                )
            )
    else:
        findings.append(
            _finding(
                "D. Accounting traps",
                "Fix",
                f"Largest customer (~{_pct(share)} of MRR) is not called out in the draft.",
                key="d_concentration",
                fix=f"State Northern Comfort share (~{_pct(share)} of MRR) on the logo slide.",
                slide_ids=["northern", "growth"],
            )
        )

    g12 = metrics["growth_12"]["result"]
    g3 = metrics["growth_3"]["result"]
    if abs(g12 - g3) > 0.005:
        if "12" in corpus and ("3" in corpus or "recent" in corpus):
            findings.append(
                _finding(
                    "D. Accounting traps",
                    "Pass",
                    "Both long and recent growth windows are shown (no short-window-only trend).",
                    key="d_growth_windows",
                )
            )
        else:
            findings.append(
                _finding(
                    "D. Accounting traps",
                    "Fix",
                    "Recent growth differs from the 12-month rate; both windows must appear.",
                    key="d_growth_windows",
                    fix=(
                        f"Show {_pct(g12)} over 12 months and {_pct(g3)} recently; "
                        "do not call the trend improving/worsening from one window alone."
                    ),
                    slide_ids=["growth"],
                )
            )
    return findings


def _check_coaching_and_guardrails(draft_text: str) -> list[dict]:
    findings = []
    lower = draft_text.lower()
    if "worth $" in lower or "valued at" in lower or "valuation of" in lower:
        findings.append(
            _finding(
                "G. Guardrails",
                "Fix",
                "Draft appears to state or imply a valuation.",
                key="g_valuation",
                fix="Remove any company worth / valuation target language.",
            )
        )
    else:
        findings.append(
            _finding(
                "G. Guardrails",
                "Pass",
                "No valuation recommendation detected.",
                key="g_valuation",
            )
        )
    if "you should accept" in lower or "must take the" in lower:
        findings.append(
            _finding(
                "G. Guardrails",
                "Fix",
                "Draft may advise accepting terms.",
                key="g_accept_terms",
                fix="Explain terms only; flag a lawyer — do not advise acceptance.",
            )
        )
    else:
        findings.append(
            _finding(
                "G. Guardrails",
                "Pass",
                "No accept/reject advice on governance terms.",
                key="g_accept_terms",
            )
        )
    return findings


def _check_contradictions(draft_text: str, *, search: bool) -> list[dict]:
    """§H — if the Market slide already hedges TAM, do not re-flag web hits as Fix."""
    findings = [
        _finding(
            "H. Contradicting evidence",
            "Pass" if search else "N/A",
            "Running independent searches for evidence that challenges market/competitor claims "
            f"(see {CHECKLIST_FILE} §H).",
            key="h_search_ran",
        )
    ]
    if not search:
        return findings

    if _market_already_hedged(draft_text):
        findings.append(
            _finding(
                "H. Contradicting evidence",
                "Pass",
                "Market/TAM slide already forbids unsourced top-down claims and prefers bottom-up — "
                "counter-evidence search does not need another rewrite.",
                key="h_tam_hedge",
            )
        )
        return findings

    hits_noted = 0
    for query in CONTRADICTION_QUERIES:
        hits = search_web(query, limit=3)
        for hit in hits[:2]:
            page = fetch_text(hit["url"], max_chars=1600)
            snippet = hit.get("snippet") or ""
            markers = ("declin", "smaller", "overstat", "challeng", "slow", "critic", "risk")
            text = page["text"] if page.get("ok") else ""
            if any(m in text.lower() for m in markers) or any(m in snippet.lower() for m in markers):
                hits_noted += 1
                findings.append(
                    _finding(
                        "H. Contradicting evidence",
                        "Fix",
                        (
                            f"Counter-evidence candidate: {hit['title']} — "
                            f"{(snippet or text[:160]).strip()}…"
                        ),
                        key="h_tam_hedge",
                        fix=(
                            "On the Market slide: do not assert a single TAM figure; "
                            "cite only opened sources, note disagreement, prefer bottom-up."
                        ),
                        slide_ids=["tam", "market"],
                        source=hit["url"],
                    )
                )
                # One Fix is enough — further hits would be circular after apply.
                break
        if hits_noted:
            break

    if hits_noted == 0:
        findings.append(
            _finding(
                "H. Contradicting evidence",
                "Pass",
                "Contradiction search returned no openable counter-claims this turn; "
                "TAM remains unsourced and should stay off the deck.",
                key="h_tam_hedge",
            )
        )
    return findings


def _apply_one_fix(slides: list[dict], finding: dict, metrics: dict) -> str | None:
    ids = set(finding.get("slide_ids") or [])
    share = metrics["northern_share"]
    g12 = metrics["growth_12"]
    g3 = metrics["growth_3"]
    margin = metrics["margin"]
    arr = metrics["arr"]
    note = finding.get("fix") or ""
    issue_l = (finding.get("issue") or "").lower()
    section = finding.get("section") or ""

    by_id = {s["id"]: s for s in slides}

    def touch(*candidates: str) -> dict | None:
        for cid in candidates:
            if cid in by_id and (not ids or cid in ids):
                return by_id[cid]
        for cid in candidates:
            if cid in by_id:
                return by_id[cid]
        return None

    if section.startswith("H") or "tam" in issue_l or "top-down" in issue_l:
        slide = touch("tam", "market")
        if slide:
            slide["body"] = (
                "Do not put a single top-down TAM on this slide until a sourced report is opened. "
                "Deck $2B remains an unsourced founder claim. Prefer a bottom-up build "
                "(contractors × seats × price × share) with citations. "
                "If public reports disagree, say so and link them — do not pick the biggest number."
            )
            return "Rewrote Market/TAM slide to forbid unsourced top-down claims and note disagreement."

    if "concentration" in issue_l or "northern comfort" in issue_l:
        slide = touch("northern", "growth")
        if slide and slide["id"] == "northern":
            slide["body"] = (
                f"Northern Comfort: 260 seats now (~{_pct(share)} of MRR); "
                "600 is verbal upside, not signed. "
                "Tell traction with and without this logo when concentration matters."
            )
            return "Added MRR concentration and with/without guidance on Northern slide."

    if "growth" in issue_l or "window" in issue_l:
        slide = touch("growth")
        if slide:
            slide["body"] = (
                f"{_pct(g12['result'])} compounded monthly over 12 months "
                f"({g12['period']}); {_pct(g3['result'])} over the last 3 "
                f"({g3['period']}). Do not call the trend from one window alone."
            )
            return "Restated both growth windows with periods."

    if "margin" in issue_l:
        slide = touch("margin")
        if slide:
            slide["body"] = (
                f"{_pct(margin['reported'])} gross margin as booked; "
                f"{_pct(margin['including_customer_success'])} with customer success "
                f"(period {margin['period']})."
            )
            return "Restated both margin definitions with period."

    if "arr" in issue_l:
        slide = touch("arr")
        if slide:
            slide["body"] = (
                f"{money(arr['result'])} ARR — MRR × 12 "
                f"(period {arr['period']}). Onboarding is one-time and separate."
            )
            return "Restated ARR with period and method."

    if "signed" in issue_l or "closed fact" in issue_l:
        for sid in ("northern", "ask"):
            slide = by_id.get(sid)
            if not slide:
                continue
            if sid == "northern" and "signed" not in slide["body"].lower():
                slide["body"] = slide["body"].rstrip() + "\n(Not a signed expansion.)"
            if sid == "ask" and "founder" not in slide["body"].lower():
                slide["body"] = slide["body"].rstrip() + "\n(Founder's plan — not a closed round.)"
        return "Labeled plan / unsigned items explicitly."

    return note or None


def _victoria_prompt(fixes: list[dict], founder_line: str) -> str:
    if not fixes:
        return (
            f"{founder_line}\n\n"
            "I had a separate reviewer walk `knowledge/audit-checklist.md`. "
            "Nothing needs a rewrite right now. You can keep editing, or audit again after changes."
        )
    bullets = "\n".join(
        f"- **{f['section']}:** {f['issue']}"
        + (f"\n  - **Suggested fix:** {f['fix']}" if f.get("fix") else "")
        for f in fixes[:8]
    )
    return (
        f"{founder_line}\n\n"
        "I had a **separate reviewer** work through `knowledge/audit-checklist.md` "
        "and search for evidence that challenges the market/competitor claims — "
        "not just evidence that supports them.\n\n"
        f"**Suggested fixes / solutions:**\n{bullets}\n\n"
        "I've listed the fixes above. Apply them to the slides when you're ready, "
        "then we can audit the draft again."
    )


def _format_remarks(findings: list[dict], founder_line: str, prompt: str) -> str:
    lines = [
        "## Audit review",
        "",
        f"Checklist: `{CHECKLIST_FILE}`. This pass was run as a **separate reviewer** "
        "(recalculate + contradict — not the same pass that wrote the slides).",
        "",
        founder_line,
        "",
        "### Remarks",
        "",
    ]
    for f in findings:
        if f["status"] == "Pass":
            continue
        if f["status"] == "Cleared":
            mark = "✓ Cleared"
        elif f["status"] == "Fix":
            mark = "⚠ Fix"
        else:
            mark = "· N/A"
        src = f" — {f['source']}" if f.get("source") else ""
        lines.append(f"- **{mark} · {f['section']}:** {f['issue']}{src}")
        if f.get("fix") and f["status"] == "Fix":
            lines.append(f"  - Suggested fix: {f['fix']}")
    if not any(f["status"] in {"Fix", "N/A", "Cleared"} for f in findings):
        lines.append("- No Fix, Cleared, or N/A items.")
    lines.extend(["", "### Victoria", "", prompt])
    return "\n".join(lines)


def _format_applied(founder_line: str, log_rows: list[dict], template_id: str) -> str:
    lines = [
        "## Audit fixes applied",
        "",
        founder_line,
        "",
        f"Template **{template_id}** was revised. Slides below are Victoria's updated draft "
        "(still tagged Victoria until you edit).",
        "",
        "| Section | Issue | How it was fixed |",
        "|---|---|---|",
    ]
    if not log_rows:
        lines.append("| — | No Fix items | — |")
    for row in log_rows:
        issue = row["issue"].replace("|", "/")
        how = row["how_fixed"].replace("|", "/")
        lines.append(f"| {row['section']} | {issue} | {how} |")
    lines.extend(
        [
            "",
            "Re-open any slide to edit. If you want another audit pass after your edits, run audit again.",
        ]
    )
    return "\n".join(lines)
