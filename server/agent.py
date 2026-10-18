"""Victoria's turn loop: route, calculate, respond, then check the reply."""

from __future__ import annotations

import json
import random
import re

from server import claude_client
from server.finance import annual_recurring_revenue, format_arr, load_income_statement, money
from server.materials import evidence_bundle, glossary_definition, investor_profiles, route, system_instructions
from server.sessions import Session
from server.financial_numbers import (
    METRIC_OPTIONS,
    answer_flashcard,
    financial_numbers_intro,
    financial_numbers_lesson,
    parse_flashcard_choice,
)
from server.funding_stage import funding_stage_pack
from server.public_resources import public_bundle
from server.snapshot import likely_investor_questions, pitch_deck_snapshot, wrong_assumptions
from server.verify import apply_checks

OPENINGS = {
    "the-lead-seed-fund": "How do you calculate ARR, and what did you leave out?",
    "the-angel-operator": "Tell me about the last customer who churned.",
    "the-strategic-investor": "How many of your customers buy from distributors like us?",
    "the-government-backed-fund": "Who prepares your financial statements?",
    "the-skeptical-partner": "Which claim on the deck would fall apart if I opened the spreadsheet?",
}

TASKS = [
    {
        "id": "funding_stage",
        "label": "Figure out what funding stage you are at",
        "aliases": (
            "funding stage",
            "what funding stage",
            "funding",
            "investors to pursue",
            "which investors",
            "what investors",
            "who should i raise",
            "who should we raise",
            "market research",
            "market size",
            "competitors",
            "comparable raises",
        ),
        "hints": (
            "stage",
            "raise",
            "seed",
            "series",
            "round",
            "safe",
            "how much to raise",
            "pursue",
            "investors",
            "terms",
            "market",
            "tam",
            "competitor",
            "comparable",
        ),
    },
    {
        "id": "financial_numbers",
        "label": "Understand financial numbers",
        "aliases": (
            "financial numbers",
            "understand financial",
            "financials",
            "metrics",
            "financial basics",
            "learn the basics",
            "learn financial",
            "teach me",
            "teach me something",
        ),
        "hints": (
            "arr",
            "mrr",
            "margin",
            "churn",
            "burn",
            "runway",
            "number",
            "numbers",
            "metric",
            "calculate",
            "teach",
            "learn",
            "basics",
            "flashcard",
            "quiz",
        ),
    },
    {
        "id": "pitch_deck",
        "label": "Analyze pitch deck",
        "aliases": ("pitch deck", "analyze pitch", "deck claims", "deck"),
        "hints": ("pitch", "claims", "slides", "deck", "tam"),
    },
    {
        "id": "investor_meeting",
        "label": "Simulate investor meeting",
        "aliases": ("simulate investor", "investor meeting", "simulate", "practice meeting", "mock investor"),
        "hints": ("practice", "mock", "roleplay", "meeting", "interview", "rehearse", "simulate"),
    },
]

PITCH_FOCUSES = [
    {
        "id": "snapshot",
        "label": "Snapshot",
        "aliases": ("snapshot", "full snapshot", "the snapshot", "quick read", "honest read"),
        "hints": ("overview", "summary", "whole", "everything", "full picture", "status", "strong"),
    },
    {
        "id": "wrong_assumptions",
        "label": "Scan for shaky assumptions",
        "aliases": (
            "wrong assumptions",
            "shaky assumptions",
            "scan for shaky",
            "assumptions",
            "highlight",
            "mistakes",
        ),
        "hints": (
            "wrong",
            "incorrect",
            "false",
            "error",
            "mistake",
            "faulty",
            "overstated",
            "rewrite",
            "shaky",
            "scan",
        ),
    },
    {
        "id": "likely_questions",
        "label": "Raise the likely investor questions",
        "aliases": (
            "likely questions",
            "likely investor questions",
            "describe likely",
            "raise the likely",
            "strong answers",
        ),
        "hints": ("question", "ask", "will ask", "practice answer", "what will they", "strong answer", "raise"),
    },
]

TASK_FILES = {
    "funding_stage": [
        "workspace/tidewell-systems/case-index.md",
        "workspace/tidewell-systems/01-overview.md",
        "workspace/tidewell-systems/03-forecast.md",
        "knowledge/glossary.md",
        "knowledge/public-resources.md",
        "workspace/tidewell-systems/glossary-examples.md",
    ],
    "financial_numbers": [
        "workspace/tidewell-systems/case-index.md",
        "workspace/tidewell-systems/01-overview.md",
        "workspace/tidewell-systems/02-financial-history.md",
        "workspace/tidewell-systems/data/README.md",
        "knowledge/glossary.md",
        "knowledge/public-resources.md",
        "workspace/tidewell-systems/glossary-examples.md",
    ],
    "pitch_deck": [
        "workspace/tidewell-systems/case-index.md",
        "workspace/tidewell-systems/01-overview.md",
        "workspace/tidewell-systems/02-financial-history.md",
        "workspace/tidewell-systems/03-forecast.md",
        "workspace/tidewell-systems/data/README.md",
        "knowledge/audit-checklist.md",
        "knowledge/glossary.md",
        "knowledge/public-resources.md",
    ],
    "investor_meeting": [
        "workspace/tidewell-systems/case-index.md",
        "workspace/tidewell-systems/01-overview.md",
        "workspace/tidewell-systems/04-investor-qa.md",
        "knowledge/investor-profiles.md",
        "knowledge/investor-qa.md",
        "knowledge/public-resources.md",
    ],
}

UNCERTAIN = re.compile(r"\b(don't know|do not know|not sure|no idea|confused)\b", re.IGNORECASE)
AMOUNT = re.compile(
    r"\$\s*(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)(?:\s*(million|m|k))?\b"
    r"|(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)\s*(million|m|k)\b",
    re.IGNORECASE,
)
FEEDBACK = re.compile(r"\b(feedback|debrief|stop practising|stop practicing)\b", re.IGNORECASE)
NUMBERED = re.compile(r"^\s*(\d{1,2})\s*[.\)\-:]\s*")


def profile_name(profile_id: str | None) -> str:
    for profile in investor_profiles():
        if profile["id"] == profile_id:
            return profile["name"].removeprefix("The ").lower()
    return "lead seed fund"


def opening(session: Session) -> dict:
    if not session.task:
        return _finish(
            session,
            _task_menu_message(),
            topic="orientation",
            files=["workspace/tidewell-systems/case-index.md"],
            calculations=[],
            user_text=None,
        )
    if session.task == "pitch_deck" and not session.pitch_focus:
        return _finish(
            session,
            _pitch_menu_message(),
            topic="pitch_deck",
            files=TASK_FILES["pitch_deck"],
            calculations=[],
            user_text=None,
        )
    if session.task == "financial_numbers" and not session.numbers_focus:
        pack = financial_numbers_intro()
        return _finish(
            session,
            pack["message"],
            topic=pack["topic"],
            files=pack["files"],
            calculations=[],
            user_text=None,
        )
    if session.task == "financial_numbers" and session.numbers_focus:
        session.numbers_card = 0
        pack = financial_numbers_lesson(session.numbers_focus, session.numbers_card)
        return _finish(
            session,
            pack["message"],
            topic=pack["topic"],
            files=pack["files"],
            calculations=pack.get("calculations", []),
            user_text=None,
        )
    if session.task == "investor_meeting" and session.mode != "investor":
        return _finish(
            session,
            _investor_menu_message(),
            topic="investor",
            files=TASK_FILES["investor_meeting"],
            calculations=[],
            user_text=None,
        )
    if session.mode == "investor":
        return _finish(
            session,
            _investor_start_message(session),
            topic="investor",
            files=TASK_FILES["investor_meeting"],
            calculations=[],
            user_text=None,
        )
    if session.task == "pitch_deck" and session.pitch_focus:
        pack = _pitch_pack(session.pitch_focus)
        return _finish(
            session,
            pack["message"],
            topic=pack["topic"],
            files=pack["files"],
            calculations=pack.get("calculations", []),
            user_text=None,
        )
    if session.task == "funding_stage":
        pack = funding_stage_pack()
        return _finish(
            session,
            pack["message"],
            topic=pack["topic"],
            files=pack["files"],
            calculations=pack.get("calculations", []),
            user_text=None,
        )
    return _finish(
        session,
        _task_start_message(session.task),
        topic=session.task or "orientation",
        files=TASK_FILES.get(session.task or "", ["workspace/tidewell-systems/case-index.md"]),
        calculations=[],
        user_text=None,
    )


def respond(session: Session, text: str) -> dict:
    text = text.strip()
    if not text:
        raise ValueError("message is empty")
    if not session.task:
        return _choose_task(session, text)
    # "Teach me something" (etc.) always opens option 2 flashcards, even mid pitch/stage work.
    if session.mode != "investor" and _asks_for_financial_teaching(text):
        return _start_financial_numbers(
            session,
            text,
            guided=session.task != "financial_numbers" or session.numbers_focus is not None,
        )
    switched = _maybe_switch_task(session, text)
    if switched is not None:
        return switched
    if session.task == "pitch_deck" and not session.pitch_focus:
        return _choose_pitch_focus(session, text)
    if session.task == "financial_numbers" and not session.numbers_focus:
        return _choose_numbers_focus(session, text)
    if session.task == "investor_meeting" and session.mode != "investor":
        return _choose_investor(session, text)
    if session.task == "pitch_deck":
        focus_switch = _match_option(text, PITCH_FOCUSES)
        if focus_switch is not None and focus_switch["id"] != session.pitch_focus:
            return _deliver_pitch_focus(session, focus_switch["id"], text)
    if session.task == "financial_numbers" and session.numbers_focus:
        total = _numbers_card_total(session.numbers_focus)
        quiz_done = session.numbers_card >= total
        if quiz_done:
            # After the deck, 1–5 / labels pick the next metric (not A–D grading).
            menu_pick = _match_option(text, METRIC_OPTIONS)
            if menu_pick is not None:
                return _deliver_numbers_focus(session, menu_pick["id"], text)
            metric_switch = _match_metric_by_name(text)
            if metric_switch is not None and metric_switch["id"] != session.numbers_focus:
                return _deliver_numbers_focus(session, metric_switch["id"], text)
        else:
            # Active flashcard: A–D / 1–4 grade; metric names can switch;
            # other free text falls through to normal coaching.
            metric_switch = _match_metric_by_name(text)
            if metric_switch is not None and metric_switch["id"] != session.numbers_focus:
                return _deliver_numbers_focus(session, metric_switch["id"], text)
            if parse_flashcard_choice(text) is not None:
                return _grade_numbers_flashcard(session, text)
    if session.mode == "investor" and FEEDBACK.search(text):
        return _release_feedback(session, text)
    topic, files = route(text)
    if session.task and session.task in TASK_FILES:
        for path in TASK_FILES[session.task]:
            if path not in files:
                files.append(path)
    session.topic = topic
    _note_uncertainty(session, text)
    calculations = _calculate(text)
    _note_claim_mismatch(session, text, calculations)
    withheld = session.mode == "investor" and not session.feedback_released
    if claude_client.configured():
        message = _claude_reply(session, text, files, calculations, withheld)
        provider = "claude"
        model = claude_client.model_name()
    else:
        message = _local_reply(session, text, topic, calculations, withheld)
        provider = "local"
        model = None
    if session.mode == "coaching":
        if provider == "claude":
            message = _attach_calculation(message, calculations)
        session.help_used = True
    if calculations:
        session.last_calculations = calculations
    return _finish(
        session,
        message,
        topic=topic,
        files=files,
        calculations=[] if withheld else calculations,
        user_text=text,
        provider=provider,
        model=model,
        withheld=withheld,
    )


def _task_menu_message() -> str:
    return "\n".join(
        [
            "Hi, I'm Victoria. I'm here to help you feel ready, not to grade you.",
            "",
            "Fundraising is a lot to carry, and nobody expects you to know all of this already. "
            "We'll go at your pace, and I'll always show you where my numbers come from.",
            "",
            "Where would you like to start?",
            "",
            "1. Figure out where you are. Stage, investors, and terms — plus market size (top-down and "
            "bottom-up), competitors, and comparable raises. Every figure will show its source.",
            "2. Learn the financial basics. I'll explain the terms investors use, in plain language, using your own numbers.",
            "3. Review your pitch deck. I'll check each claim against your data and tell you what's solid and what to tighten.",
            "4. Practice an investor meeting. Pick the kind of investor, and we'll rehearse the tough questions in a safe space.",
            "",
            "Not sure? Just tell me what's on your mind, and I'll suggest a place to begin. "
            "You can switch, pause or stop at any time.",
        ]
    )


def _task_start_message(task_id: str | None) -> str:
    if task_id == "funding_stage":
        return funding_stage_pack()["message"]
    if task_id == "financial_numbers":
        return financial_numbers_intro()["message"]
    if task_id == "pitch_deck":
        return _pitch_menu_message()
    return "What do you most need to defend in the first investor meeting?"


def _deliver_numbers_focus(session: Session, metric_id: str, text: str | None) -> dict:
    session.numbers_focus = metric_id
    session.numbers_card = 0
    session.mode = "coaching"
    pack = financial_numbers_lesson(metric_id, session.numbers_card)
    session.help_used = True
    session.last_calculations = pack.get("calculations", [])
    return _finish(
        session,
        pack["message"],
        topic=pack["topic"],
        files=pack["files"],
        calculations=pack.get("calculations", []),
        user_text=text,
    )


def _numbers_card_total(metric_id: str) -> int:
    pack = financial_numbers_lesson(metric_id, 0)
    return int(pack.get("card_total") or 0)


def _match_metric_by_name(text: str) -> dict | None:
    """Match a metric by label/alias only — not by menu number (those grade cards)."""
    stripped = text.strip().lower()
    if not stripped or stripped.isdigit() or parse_flashcard_choice(text) is not None:
        return None
    for option in METRIC_OPTIONS:
        label = option["label"].lower()
        if stripped == label or label in stripped:
            return option
        for alias in option.get("aliases", ()):
            if stripped == alias.lower() or alias.lower() in stripped:
                return option
    return None


def _grade_numbers_flashcard(session: Session, text: str) -> dict:
    metric_id = session.numbers_focus or "arr"
    result = answer_flashcard(metric_id, session.numbers_card, text)
    session.numbers_card = int(result["card_index"])
    session.mode = "coaching"
    session.help_used = True
    if result["status"] == "wrong":
        note = f"missed flashcard on {metric_id}"
        if note not in session.misunderstandings:
            session.misunderstandings.append(note)
    return _finish(
        session,
        result["message"],
        topic=result["topic"],
        files=result["files"],
        calculations=result.get("calculations", []),
        user_text=text,
    )


def _choose_numbers_focus(session: Session, text: str) -> dict:
    resolved = _resolve_menu_choice(text, METRIC_OPTIONS)
    if resolved["status"] == "matched":
        metric = resolved["option"]
        guided = resolved.get("guided")
        result = _deliver_numbers_focus(session, metric["id"], text)
        if guided:
            result["message"] = (
                f"That sounds like **{metric['label']}** — I'll go with that.\n\n" + result["message"]
            )
        return result
    if resolved["status"] == "clarify":
        choices = " or ".join(f"**{item['label']}**" for item in resolved["options"])
        return _finish(
            session,
            f"I hear you. Did you mean {choices}?\n\n" + financial_numbers_intro()["message"],
            topic="financial_numbers",
            files=TASK_FILES["financial_numbers"],
            calculations=[],
            user_text=text,
        )
    return _finish(
        session,
        "I'm not sure which metric fits — pick the closest option.\n\n"
        + financial_numbers_intro()["message"],
        topic="financial_numbers",
        files=TASK_FILES["financial_numbers"],
        calculations=[],
        user_text=text,
    )


def _pitch_menu_message() -> str:
    return "\n".join(
        [
            "Great, let's look at your deck together.",
            "",
            "How would you like to start?",
            "",
            "1. Snapshot. A quick, honest read of where your deck stands: what's strong, what needs work, "
            "and your top three questions to prepare for.",
            "2. Scan for shaky assumptions. I'll check each claim and assumption against your numbers and "
            "tell you which ones hold up, which need rewording, and which need fixing.",
            "3. Raise the likely investor questions. I'll show you the questions your deck is most likely "
            "to prompt, and we can work on your answers.",
            "",
            "You can do all three in any order. If your deck isn't handy, share the main claims or paste "
            "the text, and we'll start from there.",
        ]
    )


def _pitch_pack(focus_id: str) -> dict:
    if focus_id == "wrong_assumptions":
        return wrong_assumptions()
    if focus_id == "likely_questions":
        return likely_investor_questions()
    return pitch_deck_snapshot()


def _deliver_pitch_focus(session: Session, focus_id: str, text: str | None) -> dict:
    session.pitch_focus = focus_id
    session.mode = "coaching"
    pack = _pitch_pack(focus_id)
    session.help_used = True
    session.last_calculations = pack.get("calculations", [])
    return _finish(
        session,
        pack["message"],
        topic=pack["topic"],
        files=pack["files"],
        calculations=pack.get("calculations", []),
        user_text=text,
        offers_deck_draft=bool(pack.get("offers_deck_draft")),
    )


def _choose_pitch_focus(session: Session, text: str) -> dict:
    resolved = _resolve_menu_choice(text, PITCH_FOCUSES)
    if resolved["status"] == "matched":
        focus = resolved["option"]
        guided = resolved.get("guided")
        if guided:
            pack = _pitch_pack(focus["id"])
            session.pitch_focus = focus["id"]
            session.mode = "coaching"
            session.help_used = True
            session.last_calculations = pack.get("calculations", [])
            message = (
                f"That sounds like **{focus['label']}** — I'll go with that.\n\n" + pack["message"]
            )
            return _finish(
                session,
                message,
                topic=pack["topic"],
                files=pack["files"],
                calculations=pack.get("calculations", []),
                user_text=text,
                offers_deck_draft=bool(pack.get("offers_deck_draft")),
            )
        return _deliver_pitch_focus(session, focus["id"], text)
    if resolved["status"] == "clarify":
        options = resolved["options"]
        choices = " or ".join(f"**{item['label']}**" for item in options)
        return _finish(
            session,
            f"I hear you. Did you mean {choices}?\n\n" + _pitch_menu_message(),
            topic="pitch_deck",
            files=TASK_FILES["pitch_deck"],
            calculations=[],
            user_text=text,
        )
    return _finish(
        session,
        "I'm not sure which path fits — pick the closest option below.\n\n" + _pitch_menu_message(),
        topic="pitch_deck",
        files=TASK_FILES["pitch_deck"],
        calculations=[],
        user_text=text,
    )


def _investor_menu_message() -> str:
    lines = [
        "I'll play an investor and hold the calculation until you ask for feedback.",
        "Which one? Reply with a number, or say \"surprise me\":",
        "",
    ]
    for index, profile in enumerate(investor_profiles(), start=1):
        lines.append(f"{index}. {profile['name']}")
    return "\n".join(lines)


def _investor_start_message(session: Session) -> str:
    question = OPENINGS.get(session.investor_profile or "", OPENINGS["the-lead-seed-fund"])
    return f"Playing the {profile_name(session.investor_profile)}.\n\n{question}"


def _asks_for_financial_teaching(text: str) -> bool:
    """True when the founder wants option-2 style teaching (flashcards / basics), not free-form chat."""
    lowered = text.lower().strip()
    phrases = (
        "teach me something",
        "teach me",
        "teach something",
        "teach us",
        "learn the financial",
        "learn financial",
        "financial basics",
        "learn the basics",
        "learn something",
        "explain the metrics",
        "explain metrics",
        "quiz me",
        "flashcard",
        "flash cards",
        "multiple choice",
        "help me learn",
        "walk me through the numbers",
        "walk me through my numbers",
        "understand the numbers",
        "understand my numbers",
    )
    if any(phrase in lowered for phrase in phrases):
        return True
    if "teach" in lowered and any(
        word in lowered for word in ("me", "us", "something", "number", "metric", "basics", "finance")
    ):
        return True
    return False


def _start_financial_numbers(session: Session, text: str | None, *, guided: bool = False) -> dict:
    """Enter the option-2 umbrella: metric menu + multiple-choice flashcards."""
    session.task = "financial_numbers"
    session.mode = "coaching"
    session.pitch_focus = None
    session.numbers_focus = None
    session.numbers_card = 0
    session.investor_profile = None
    pack = financial_numbers_intro()
    preface = (
        "That sounds like **learning the financial basics** — I'll teach with flashcards "
        "(multiple choice), same as option 2 on the menu.\n\n"
        if guided
        else ""
    )
    return _finish(
        session,
        preface + pack["message"],
        topic=pack["topic"],
        files=pack["files"],
        calculations=[],
        user_text=text,
    )


def _maybe_switch_task(session: Session, text: str) -> dict | None:
    """If the founder clearly asks for a different menu task, switch focus."""
    if session.mode == "investor":
        return None
    if _asks_for_financial_teaching(text):
        return _start_financial_numbers(session, text, guided=True)
    match = _match_option(text, TASKS)
    if match is None or match["id"] == session.task:
        return None
    lowered = text.lower()
    explicit = any(
        word in lowered
        for word in ("now", "instead", "switch", "analyze", "simulate", "want to", "let's", "lets", "teach")
    )
    if not explicit and match["label"].lower() not in lowered:
        return None
    return _choose_task(session, text)


def _asks_which_investors_to_pursue(text: str) -> bool:
    """True when the founder wants advice on which investors/stage to pursue — not a mock meeting."""
    lowered = text.lower()
    if any(
        phrase in lowered
        for phrase in (
            "investors should i pursue",
            "investor should i pursue",
            "investors to pursue",
            "investor to pursue",
            "which investors",
            "what investors",
            "which investor",
            "what investor",
            "who should i raise",
            "who should we raise",
            "pursue based on",
            "based on my finances",
            "based on our finances",
            "based on my numbers",
            "based on our numbers",
        )
    ):
        return True
    wants_pursue = "pursue" in lowered or "who should" in lowered
    about_investors = "investor" in lowered or "investors" in lowered
    mockish = any(
        word in lowered for word in ("simulate", "practice", "mock", "roleplay", "rehearse", "meeting")
    )
    return wants_pursue and about_investors and not mockish


def _start_funding_stage(session: Session, text: str | None, *, guided: bool = False) -> dict:
    session.task = "funding_stage"
    session.mode = "coaching"
    session.pitch_focus = None
    session.numbers_focus = None
    session.numbers_card = 0
    session.investor_profile = None
    pack = funding_stage_pack()
    session.help_used = True
    session.last_calculations = pack.get("calculations", [])
    preface = (
        "That sounds like **which investors / funding stage to pursue** — I'll go with that.\n\n"
        if guided
        else ""
    )
    return _finish(
        session,
        preface + pack["message"],
        topic=pack["topic"],
        files=pack["files"],
        calculations=pack.get("calculations", []),
        user_text=text,
    )


def _choose_task(session: Session, text: str) -> dict:
    if _asks_which_investors_to_pursue(text):
        return _start_funding_stage(session, text, guided=True)
    if _asks_for_financial_teaching(text):
        return _start_financial_numbers(session, text, guided=True)
    resolved = _resolve_menu_choice(text, TASKS)
    if resolved["status"] == "clarify":
        options = resolved["options"]
        if _asks_which_investors_to_pursue(text):
            return _start_funding_stage(session, text, guided=True)
        choices = " or ".join(f"**{item['label']}**" for item in options)
        return _finish(
            session,
            f"I hear you. Did you mean {choices}?\n\n" + _task_menu_message(),
            topic="orientation",
            files=["workspace/tidewell-systems/case-index.md"],
            calculations=[],
            user_text=text,
        )
    if resolved["status"] != "matched":
        return _finish(
            session,
            "I'm not sure which fits best — pick the closest option below.\n\n" + _task_menu_message(),
            topic="orientation",
            files=["workspace/tidewell-systems/case-index.md"],
            calculations=[],
            user_text=text,
        )
    task = resolved["option"]
    guided = resolved.get("guided")
    session.task = task["id"]
    session.pitch_focus = None
    session.numbers_focus = None
    session.numbers_card = 0
    if task["id"] == "investor_meeting":
        if _asks_which_investors_to_pursue(text):
            return _start_funding_stage(session, text, guided=True)
        session.mode = "chooser"
        session.investor_profile = None
        preface = f"That sounds like **{task['label']}** — I'll go with that.\n\n" if guided else ""
        return _finish(
            session,
            preface + _investor_menu_message(),
            topic="investor",
            files=TASK_FILES["investor_meeting"],
            calculations=[],
            user_text=text,
        )
    if task["id"] == "pitch_deck":
        session.mode = "coaching"
        preface = f"That sounds like **{task['label']}** — I'll go with that.\n\n" if guided else ""
        return _finish(
            session,
            preface + _pitch_menu_message(),
            topic="pitch_deck",
            files=TASK_FILES["pitch_deck"],
            calculations=[],
            user_text=text,
        )
    if task["id"] == "financial_numbers":
        return _start_financial_numbers(session, text, guided=guided)
    session.mode = "coaching"
    preface = f"That sounds like **{task['label']}** — I'll go with that.\n\n" if guided else ""
    if task["id"] == "funding_stage":
        pack = funding_stage_pack()
        session.help_used = True
        session.last_calculations = pack.get("calculations", [])
        return _finish(
            session,
            preface + pack["message"],
            topic=pack["topic"],
            files=pack["files"],
            calculations=pack.get("calculations", []),
            user_text=text,
        )
    return _finish(
        session,
        preface + _task_start_message(task["id"]),
        topic=task["id"],
        files=TASK_FILES[task["id"]],
        calculations=[],
        user_text=text,
    )


def _choose_investor(session: Session, text: str) -> dict:
    if _asks_which_investors_to_pursue(text):
        return _start_funding_stage(session, text, guided=True)
    profiles = investor_profiles()
    options = [
        {
            "id": item["id"],
            "label": item["name"],
            "aliases": (item["name"], item["id"], item["name"].removeprefix("The ")),
            "hints": tuple(
                part
                for part in re.split(r"[^a-z0-9]+", item["name"].lower())
                if len(part) > 3 and part not in {"investor", "investors", "fund", "partner"}
            ),
        }
        for item in profiles
    ]
    lowered = text.lower()
    if "surprise" in lowered or "random" in lowered or lowered.strip() == "any":
        chosen = random.choice(profiles)
    else:
        resolved = _resolve_menu_choice(text, options)
        if resolved["status"] == "clarify":
            choices = " or ".join(f"**{item['label']}**" for item in resolved["options"])
            return _finish(
                session,
                f"I hear you. Did you mean {choices}?\n\n"
                + "Or reply with a number / \"surprise me\":\n"
                + "\n".join(f"{i}. {p['name']}" for i, p in enumerate(profiles, start=1)),
                topic="investor",
                files=TASK_FILES["investor_meeting"],
                calculations=[],
                user_text=text,
            )
        if resolved["status"] != "matched":
            return _finish(
                session,
                "I'm not sure which investor fits — pick one, or say \"surprise me\".\n\n"
                + "\n".join(f"{i}. {p['name']}" for i, p in enumerate(profiles, start=1)),
                topic="investor",
                files=TASK_FILES["investor_meeting"],
                calculations=[],
                user_text=text,
            )
        chosen = next(item for item in profiles if item["id"] == resolved["option"]["id"])
        guided = resolved.get("guided")
        session.investor_profile = chosen["id"]
        session.mode = "investor"
        session.feedback_released = False
        preface = (
            f"That sounds like **{chosen['name']}** — I'll play that.\n\n" if guided else ""
        )
        return _finish(
            session,
            preface + _investor_start_message(session),
            topic="investor",
            files=TASK_FILES["investor_meeting"],
            calculations=[],
            user_text=text,
        )
    session.investor_profile = chosen["id"]
    session.mode = "investor"
    session.feedback_released = False
    return _finish(
        session,
        _investor_start_message(session),
        topic="investor",
        files=TASK_FILES["investor_meeting"],
        calculations=[],
        user_text=text,
    )


def _match_option(text: str, options: list[dict]) -> dict | None:
    stripped = text.strip()
    numbered = NUMBERED.match(stripped)
    if numbered:
        index = int(numbered.group(1))
        if 1 <= index <= len(options):
            return options[index - 1]
        return None
    if stripped.isdigit():
        index = int(stripped)
        if 1 <= index <= len(options):
            return options[index - 1]
        return None
    lowered = stripped.lower()
    for option in options:
        label = option["label"].lower()
        if lowered == label or label in lowered:
            return option
        for alias in option.get("aliases", ()):
            if lowered == alias.lower() or alias.lower() in lowered:
                return option
    return None


_STOPWORDS = {
    "what",
    "with",
    "that",
    "this",
    "from",
    "your",
    "you",
    "are",
    "for",
    "the",
    "and",
    "out",
    "how",
    "did",
    "does",
    "have",
    "want",
    "need",
    "help",
    "about",
    "into",
}


def _score_option(text: str, option: dict) -> int:
    lowered = text.lower()
    score = 0
    label = option["label"].lower()
    if label in lowered:
        score += 8
    for word in re.findall(r"[a-z0-9]+", label):
        if len(word) > 3 and word not in _STOPWORDS and _word_in(word, lowered):
            score += 2
    for alias in option.get("aliases", ()):
        alias_l = alias.lower()
        if alias_l in lowered:
            score += 6
        else:
            for part in alias_l.split():
                if len(part) > 3 and part not in _STOPWORDS and _word_in(part, lowered):
                    score += 2
    for hint in option.get("hints", ()):
        hint_l = hint.lower()
        if " " in hint_l:
            if hint_l in lowered:
                score += 4
        elif _word_in(hint_l, lowered):
            score += 3
    return score


def _word_in(word: str, text: str) -> bool:
    """Match a whole word, allowing a simple trailing plural s."""
    return bool(re.search(rf"\b{re.escape(word)}s?\b", text))


def _resolve_menu_choice(text: str, options: list[dict]) -> dict:
    """Match a free-text menu reply: exact, guided, clarify, or unclear."""
    exact = _match_option(text, options)
    if exact is not None:
        return {"status": "matched", "option": exact, "guided": False}
    ranked = sorted(
        ((_score_option(text, option), option) for option in options),
        key=lambda item: item[0],
        reverse=True,
    )
    if not ranked or ranked[0][0] <= 0:
        return {"status": "unclear"}
    top_score, top = ranked[0]
    second_score = ranked[1][0] if len(ranked) > 1 else 0
    if top_score >= 3 and top_score >= second_score + 2:
        return {"status": "matched", "option": top, "guided": True}
    close = [option for score, option in ranked if score > 0 and score >= top_score - 1]
    if len(close) >= 2:
        return {"status": "clarify", "options": close[:2]}
    if top_score >= 3:
        return {"status": "matched", "option": top, "guided": True}
    return {"status": "unclear"}


def _claude_reply(session: Session, text: str, files: list[str], calculations: list[dict], withheld: bool) -> str:
    prior = [{"role": item["role"], "content": item["content"]} for item in session.history if item["role"] in {"user", "assistant"}]
    visible_calculations = [] if withheld else calculations
    packet = {
        "mode": session.mode,
        "task": session.task,
        "pitch_focus": session.pitch_focus,
        "numbers_focus": session.numbers_focus,
        "investor_profile": session.investor_profile,
        "help_used": session.help_used,
        "misunderstandings": session.misunderstandings,
        "calculations": visible_calculations,
        "calculations_withheld": withheld,
    }
    focus = {
        "funding_stage": (
            "Focus on funding stage, prior SAFEs, the current raise, market research "
            "(top-down/bottom-up size, competitors, comparable raises), and terms. "
            "Every figure must keep its source tag (public URL, founder plan, historical books, or upload). "
            "Do not invent market or raise numbers that were not fetched or in the files."
        ),
        "financial_numbers": (
            f"Teach with flashcards / multiple choice. Current metric focus: {session.numbers_focus or 'intro'}; "
            f"card index: {session.numbers_card}. "
            "If they already answered a card, the code graded it — reinforce briefly, do not replace the insight. "
            "Keep replies short."
        ),
        "pitch_deck": (
            "Help the founder fix deck weaknesses and reduce stress. "
            f"Current pitch focus: {session.pitch_focus or 'menu'}. "
            "Stay on that focus unless they pick another (snapshot / wrong assumptions / likely questions). "
            "Keep replies short."
        ),
        "investor_meeting": "Stay in character as the selected investor. Do not teach until feedback is requested.",
    }.get(session.task or "", "Follow the founder's selected task.")
    public = public_bundle(topic_for_public(session, text), fetch=True, fetch_limit=3)
    founder = (
        f"Founder said:\n{text}\n\n"
        f"Session state:\n{json.dumps(packet, indent=2)}\n\n"
        f"Task focus: {focus}\n\n"
        "Reply briefly: a few short sentences or a small table. One question at the end. "
        "Use a calculation only if it appears above. "
        "If calculations_withheld is true, do not state the hidden figure. "
        "When you use a public resource, cite title + publisher + URL. "
        "Only quote a fact from a fetched page below; otherwise link out.\n\n"
        f"Opened files:\n{evidence_bundle(files, limit=4000)}"
    )
    if public:
        founder += f"\n\n{public}"
    prior.append({"role": "user", "content": founder})
    return claude_client.complete(system_instructions(), prior)


def topic_for_public(session: Session, text: str) -> str | None:
    """Pick which public-resource set to fetch for this turn."""
    if session.task in {"funding_stage", "pitch_deck", "investor_meeting"}:
        return session.task
    lowered = text.lower()
    if any(word in lowered for word in ("term sheet", "liquidation", "pro-rata", "drag-along", "safe", "nvca")):
        return "terms"
    if any(word in lowered for word in ("seed", "raise", "fundraising", "angel", "venture")):
        return "seed"
    if session.numbers_focus in {"arr", "growth", "margin", "churn", "runway"}:
        return session.numbers_focus
    if session.topic in {"valuation", "investor", "market", "runway", "churn"}:
        return session.topic
    return None


def _local_reply(session: Session, text: str, topic: str, calculations: list[dict], withheld: bool) -> str:
    if withheld:
        if topic == "valuation":
            return "I won't name a price. Are you asking about pre-money, post-money, or dilution?"
        if calculations:
            return "I'll hold the calculation until you ask for feedback. What did you leave out of the ARR you would say out loud?"
        return "What in that answer comes from the books, and what is still an assumption?"
    if session.task == "funding_stage" and topic in {"orientation", "funding_stage", "investor", "market"}:
        return (
            "Practise the one-liner from the pack, or pick one term to unpack: "
            "liquidation preference, pro-rata, protective provisions, or drag-along."
        )
    if session.task == "pitch_deck" and not calculations:
        if not session.pitch_focus:
            return _pitch_menu_message()
        return "Want to go deeper on ARR, growth, or margin — or pick another deck option (1–3)?"
    if topic == "valuation":
        return (
            "I can't recommend a valuation. Pre-money is before new money; post-money includes it; "
            "dilution is the ownership drop when new shares are issued.\n\n"
            "Which of those three do you want to explain?"
        )
    if topic == "runway":
        return (
            "Runway is cash ÷ monthly net burn. Cash isn't in the loaded income statement, so I can't calculate it.\n\n"
            "Want the definition of burn, or which file would supply cash?"
        )
    if topic == "churn":
        return (
            "Logo churn is customers lost ÷ customers at month start. "
            "The customer file isn't loaded, so I can't calculate it.\n\n"
            "Formula, or how to talk about the deck claim without a number?"
        )
    if calculations:
        mismatch = " Your figure doesn't match." if _mismatches(text, calculations) else ""
        return (
            f"ARR is {money(calculations[0]['result'])} "
            f"(subscription × 12 for {calculations[0]['period']}; onboarding left out). "
            f"*(Historical)*{mismatch}\n\n"
            "What would you include or leave out when you say it out loud?"
        )
    if topic == "forecast":
        return (
            "The forecast is the founders' plan, not closed results — and there's no forecast CSV in data/.\n\n"
            "Which assumption do you want to pressure-test?"
        )
    return (
        "I don't have that calculation yet, and I won't estimate it.\n\n"
        "Historical numbers, forecast, or an investor question?"
    )


def _release_feedback(session: Session, text: str) -> dict:
    session.feedback_released = True
    calculations = session.last_calculations
    lines = ["Feedback:"]
    if session.help_used:
        lines.append("You used coaching during the round.")
    if calculations and "result" in calculations[0]:
        lines.append(
            f"ARR from the books: {money(calculations[0]['result'])}. *(Historical)*"
        )
        if any("does not match" in item for item in session.misunderstandings):
            lines.append("A figure you said didn't match.")
    else:
        lines.append("No metric was calculated this round.")
    if session.misunderstandings:
        lines.append("Still open: " + "; ".join(session.misunderstandings[-2:]) + ".")
    lines.append("Next: restate it using only the calculated figure.")
    message = "\n".join(lines)
    session.practice_results.append(
        {
            "investor_profile": session.investor_profile,
            "help_used": session.help_used,
            "topic": session.topic,
        }
    )
    return _finish(
        session,
        message,
        topic=session.topic or "investor",
        files=["knowledge/investor-qa.md"],
        calculations=calculations,
        user_text=text,
        provider="local",
        model=None,
        withheld=False,
    )


def _calculate(text: str) -> list[dict]:
    lowered = text.lower()
    if not any(word in lowered for word in ("arr", "mrr", "recurring", "subscription")):
        return []
    rows = load_income_statement()
    return [annual_recurring_revenue(rows)]


def _attach_calculation(message: str, calculations: list[dict]) -> str:
    ready = [item for item in calculations if item.get("metric") == "ARR" and "result" in item]
    if not ready:
        return message
    # Skip the appendix if Claude already stated the ARR figure.
    if money(ready[0]["result"]) in message or "Calculated in code:" in message:
        return message
    short = (
        f"Calculated: ARR {money(ready[0]['result'])} "
        f"({ready[0]['period']}, subscription × 12). *(Historical)*"
    )
    return message.rstrip() + "\n\n" + short


def _note_uncertainty(session: Session, text: str) -> None:
    if UNCERTAIN.search(text):
        note = f"uncertain about {session.topic or 'the current question'}"
        if note not in session.misunderstandings:
            session.misunderstandings.append(note)


def _amount_values(text: str) -> list[float]:
    found = []
    for match in AMOUNT.finditer(text):
        raw = match.group(1) or match.group(3)
        unit = (match.group(2) or match.group(4) or "").lower()
        value = float(raw.replace(",", ""))
        if unit in {"million", "m"}:
            value *= 1_000_000
        elif unit == "k":
            value *= 1_000
        found.append(value)
    return found


def _mismatches(text: str, calculations: list[dict]) -> bool:
    if not calculations or "result" not in calculations[0]:
        return False
    target = calculations[0]["result"]
    for value in _amount_values(text):
        if abs(value - target) > max(1, abs(target) * 0.01):
            return True
    return False


def _note_claim_mismatch(session: Session, text: str, calculations: list[dict]) -> None:
    if _mismatches(text, calculations):
        note = f"stated figure does not match calculated {calculations[0]['metric']}"
        if note not in session.misunderstandings:
            session.misunderstandings.append(note)


def _finish(
    session: Session,
    message: str,
    topic: str,
    files: list[str],
    calculations: list[dict],
    user_text: str | None,
    provider: str = "local",
    model: str | None = None,
    withheld: bool = False,
    offers_deck_draft: bool = False,
) -> dict:
    message, verification = apply_checks(message)
    if user_text is not None:
        session.history.append({"role": "user", "content": user_text})
    session.history.append({"role": "assistant", "content": message})
    if calculations:
        session.last_calculations = calculations
    public_calculations = [] if withheld else calculations
    return {
        "session_id": session.id,
        "provider": provider,
        "model": model,
        "message": message,
        "mode": session.mode,
        "task": session.task,
        "pitch_focus": session.pitch_focus,
        "numbers_focus": session.numbers_focus,
        "investor_profile": session.investor_profile,
        "topic": topic,
        "routed_files": files,
        "calculations": public_calculations,
        "calculations_withheld": withheld,
        "help_used": session.help_used,
        "misunderstandings": list(session.misunderstandings),
        "practice_results": list(session.practice_results),
        "verification": verification,
        "company_id": session.company_id,
        "offers_deck_draft": offers_deck_draft,
    }
