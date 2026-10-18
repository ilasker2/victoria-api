"""Load rules and knowledge. The conversation tests and source workbook are not coaching inputs."""

from __future__ import annotations

import re

from server.paths import KNOWLEDGE, RULES, WORKSPACE

RULE_FILES = [
    "00-persona-and-mission.mdc",
    "05-core-principles.mdc",
    "10-coaching-method.mdc",
    "20-knowledge-routing.mdc",
    "30-calculation-standards.mdc",
    "40-output-formats.mdc",
    "50-guardrails.mdc",
]

# Topic id, keywords, files relative to the project root.
ROUTES = [
    (
        "arr",
        ("arr", "mrr", "recurring", "subscription", "onboarding"),
        [
            "knowledge/glossary.md",
            "workspace/tidewell-systems/glossary-examples.md",
            "workspace/tidewell-systems/01-overview.md",
            "workspace/tidewell-systems/02-financial-history.md",
            "workspace/tidewell-systems/data/README.md",
        ],
    ),
    (
        "runway",
        ("runway", "burn", "cash"),
        [
            "knowledge/glossary.md",
            "workspace/tidewell-systems/glossary-examples.md",
            "workspace/tidewell-systems/02-financial-history.md",
            "workspace/tidewell-systems/03-forecast.md",
            "workspace/tidewell-systems/data/README.md",
        ],
    ),
    (
        "margin",
        ("margin", "gross profit", "cogs", "cost of revenue"),
        [
            "knowledge/glossary.md",
            "workspace/tidewell-systems/glossary-examples.md",
            "workspace/tidewell-systems/02-financial-history.md",
            "workspace/tidewell-systems/data/README.md",
        ],
    ),
    (
        "churn",
        ("churn", "retention", "nrr", "grr"),
        [
            "knowledge/glossary.md",
            "knowledge/investor-qa.md",
            "workspace/tidewell-systems/glossary-examples.md",
            "workspace/tidewell-systems/02-financial-history.md",
            "workspace/tidewell-systems/data/README.md",
        ],
    ),
    (
        "forecast",
        ("forecast", "hiring", "assumption", "plan"),
        [
            "workspace/tidewell-systems/03-forecast.md",
            "workspace/tidewell-systems/02-financial-history.md",
            "workspace/tidewell-systems/data/README.md",
        ],
    ),
    (
        "valuation",
        ("valuation", "pre-money", "post-money", "dilution", "safe", "ownership"),
        [
            "knowledge/glossary.md",
            "knowledge/public-resources.md",
            "workspace/tidewell-systems/01-overview.md",
            "workspace/tidewell-systems/glossary-examples.md",
        ],
    ),
    (
        "investor",
        ("investor", "practice", "seed", "pitch", "meeting", "term sheet", "liquidation", "pro-rata"),
        [
            "knowledge/investor-profiles.md",
            "knowledge/investor-qa.md",
            "knowledge/public-resources.md",
            "workspace/tidewell-systems/04-investor-qa.md",
            "workspace/tidewell-systems/01-overview.md",
        ],
    ),
    (
        "platform",
        ("june", "franco", "rocco", "platform"),
        ["knowledge/june-platform.md"],
    ),
    (
        "market",
        ("tam", "market", "benchmark", "sr&ed", "sred"),
        [
            "knowledge/public-resources.md",
            "knowledge/glossary.md",
            "workspace/tidewell-systems/01-overview.md",
        ],
    ),
]


def read_text(relative: str) -> str:
    path = _resolve(relative)
    if path is None or not path.exists() or path.suffix.lower() not in {".md", ".mdc"}:
        raise FileNotFoundError(relative)
    if "tests" in path.parts or path.parent.name == "source":
        raise FileNotFoundError(relative)
    return path.read_text(encoding="utf-8")


def _resolve(relative: str):
    if relative.startswith("knowledge/"):
        return KNOWLEDGE / relative.removeprefix("knowledge/")
    if relative.startswith("workspace/tidewell-systems/"):
        return WORKSPACE / relative.removeprefix("workspace/tidewell-systems/")
    if relative.startswith(".cursor/rules/"):
        return RULES / relative.removeprefix(".cursor/rules/")
    return None


def system_instructions() -> str:
    parts = []
    for name in RULE_FILES:
        parts.append((RULES / name).read_text(encoding="utf-8"))
    parts.append(
        "\n".join(
            [
                "# Runtime",
                "You are in a live session with one founder.",
                "Ask one question at a time.",
                "Keep every reply short: bare minimum for critical understanding. Prefer a few short sentences or a small table. Do not lecture or repeat the same number in multiple forms.",
                "Go deeper only if the founder asks.",
                "If a calculations object is provided, use those figures exactly. Do not recompute them and do not replace them.",
                "If a figure is not in the calculations object or the opened files, say it was not provided.",
                "Do not quote tests/conversations. Do not read source PDFs or the original workbook yourself.",
                "Do not recommend a valuation, a range, or a target.",
                "Label historical figures and forecast figures differently.",
                "Sessions start with a task menu. Once the founder picks a task, stay on that task.",
                "Funding-stage work may already include a code-built stage suggestion, investor types, term explanations, "
                "and market research (top-down/bottom-up size, competitors, comparable raises). "
                "Keep every figure's source tag: public URL, founder's plan, historical books, or upload (missing).",
                "Explain investor rights and ask clarifying questions — do not advise whether to accept terms. Flag a lawyer for term sheets.",
                "When public resource pages are fetched into the prompt, use them for seed fundraising and term vocabulary.",
                "Cite public sources by title, publisher, and URL. Label US data/forms as US when used for a Canadian company.",
                "If a page was not fetched or fetch failed, link the resource — do not invent its contents or quote a benchmark from memory.",
                "Pitch-deck work starts with a short menu: Snapshot, Scan for shaky assumptions, or Raise the likely investor questions.",
                "Goal: fix the founder's concerns and reduce stress. Lead with what to say instead.",
                "Explain or drill into the code-built pack already shown; do not invent replacement figures.",
                "Financial-numbers work uses flashcards with multiple choice: wrong → short feedback and retry; right → the insight / meeting line. Do not ask for long free-text answers first.",
                "Coaching mode may explain and show the calculation.",
                "Investor mode asks and challenges. It does not teach or reveal the calculation until the founder asks for feedback.",
                "End with one concrete next step or one question — never both a long summary and a list of extras.",
            ]
        )
    )
    return "\n\n".join(parts)


def route(text: str) -> tuple[str, list[str]]:
    lowered = text.lower()
    chosen = "orientation"
    files = ["workspace/tidewell-systems/case-index.md"]
    for topic, words, paths in ROUTES:
        if any(word in lowered for word in words):
            chosen = topic
            files = list(paths)
            break
    if "workspace/tidewell-systems/case-index.md" not in files:
        files.append("workspace/tidewell-systems/case-index.md")
    return chosen, files


def glossary_definition(term: str) -> str | None:
    table = (KNOWLEDGE / "glossary.md").read_text(encoding="utf-8")
    pattern = re.compile(rf"\| \*\*{re.escape(term)}\*\*.*?\| (.*?) \|", re.IGNORECASE)
    match = pattern.search(table)
    if not match:
        return None
    return re.sub(r"\s+", " ", match.group(1)).strip()


def evidence_bundle(files: list[str], limit: int = 7000) -> str:
    chunks = []
    skipped = []
    seen: set[str] = set()
    for relative in files:
        if relative in seen:
            continue
        seen.add(relative)
        try:
            text = read_text(relative).strip()
        except FileNotFoundError:
            skipped.append(relative)
            continue
        if len(text) > limit:
            text = text[:limit] + "\n\n[truncated]"
        chunks.append(f"## File: {relative}\n\n{text}")
    if skipped:
        chunks.append(
            "## Files not opened\n\n"
            + "\n".join(f"- `{path}` (missing, blocked, or not a markdown coaching file)" for path in skipped)
            + "\n\nUse calculations in session state for figures from the income-statement CSV. "
            "Do not invent contents for skipped files."
        )
    return "\n\n".join(chunks)


def investor_profiles() -> list[dict]:
    text = (KNOWLEDGE / "investor-profiles.md").read_text(encoding="utf-8")
    profiles = []
    for match in re.finditer(r"^## \d+\. (.+)$", text, re.MULTILINE):
        name = match.group(1).strip()
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        profiles.append({"id": slug, "name": name})
    return profiles
