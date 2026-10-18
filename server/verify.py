"""Deterministic checks applied before a reply is returned."""

from __future__ import annotations

import re

VALUATION = re.compile(
    r"(recommend(?:s|ed|ing)? a valuation|target valuation|you should (?:raise|be valued) at|"
    r"the company is worth|i(?:'d| would) value|valuation of \$)",
    re.IGNORECASE,
)

SAFE_VALUATION_REPLY = (
    "I can't recommend a valuation. I can explain what pre-money and post-money mean, "
    "and what a round does to ownership, once a term sheet states those figures. "
    "The price comes from the negotiation, not from me.\n\n"
    "Which term do you want to be able to explain: pre-money, post-money, or dilution?"
)


def verify(message: str) -> dict:
    checks = []
    ok = True
    if message.strip():
        checks.append("non_empty")
    else:
        ok = False
        checks.append("empty")
    if VALUATION.search(message):
        ok = False
        checks.append("valuation_recommendation")
    else:
        checks.append("no_valuation_recommendation")
    return {"ok": ok, "checks": checks}


def apply_checks(message: str) -> tuple[str, dict]:
    result = verify(message)
    if "valuation_recommendation" in result["checks"]:
        result["revised"] = True
        return SAFE_VALUATION_REPLY, result
    result["revised"] = False
    return message, result
