"""Parse knowledge/public-resources.md and select links for coaching topics."""

from __future__ import annotations

import re
from functools import lru_cache

from server.paths import KNOWLEDGE
from server.web_fetch import fetch_many, format_fetched

# Topics that should pull public links into the model context.
TOPIC_RESOURCES = {
    "funding_stage": (8, 9, 14, 15, 16, 17, 18, 19, 20, 22),
    "seed": (8, 9, 15, 16),
    "terms": (17, 18),
    "safe": (17, 18),
    "valuation": (17, 18, 8),
    "investor": (8, 9, 15, 16, 11),
    "investor_meeting": (8, 9, 11, 15),
    "pitch_deck": (1, 2, 7, 8, 15),
    "arr": (11,),
    "growth": (11, 13),
    "margin": (11,),
    "churn": (11,),
    "runway": (10, 12),
    "market": (14, 19, 20),
    "platform": (),
}

# Prefer fetching these when bandwidth is limited (seed + terms first).
FETCH_PRIORITY = (8, 9, 17, 18, 15, 16, 11, 10, 12, 19)


@lru_cache(maxsize=1)
def load_resources() -> list[dict]:
    text = (KNOWLEDGE / "public-resources.md").read_text(encoding="utf-8")
    resources = []
    for match in re.finditer(
        r"^\|\s*(\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$",
        text,
        re.MULTILINE,
    ):
        number = int(match.group(1))
        title = _clean_cell(match.group(2))
        publisher = _clean_cell(match.group(3))
        summary = _clean_cell(match.group(4))
        link = _clean_link(match.group(5))
        if not link.startswith("http"):
            continue
        resources.append(
            {
                "id": number,
                "title": title,
                "publisher": publisher,
                "summary": summary,
                "url": link,
            }
        )
    return resources


def resources_for_topic(topic: str | None) -> list[dict]:
    if not topic:
        return []
    wanted = TOPIC_RESOURCES.get(topic, ())
    if not wanted:
        # Keyword fallback for free-text topics.
        lowered = topic.lower()
        if any(word in lowered for word in ("term", "safe", "liquidation", "pro-rata", "drag")):
            wanted = TOPIC_RESOURCES["terms"]
        elif any(word in lowered for word in ("seed", "raise", "fund", "angel")):
            wanted = TOPIC_RESOURCES["seed"]
        else:
            return []
    by_id = {item["id"]: item for item in load_resources()}
    return [by_id[i] for i in wanted if i in by_id]


def format_resource_directory(resources: list[dict]) -> str:
    if not resources:
        return ""
    lines = ["## Public resources (cite by name and URL when used)", ""]
    for item in resources:
        lines.append(
            f"- **#{item['id']} {item['title']}** ({item['publisher']}): {item['summary']} "
            f"— {item['url']}"
        )
    lines.append("")
    lines.append(
        "Only state a fact from a page if that page was fetched below. "
        "Otherwise point the founder to the link. Label US sources as US data."
    )
    return "\n".join(lines)


def citation(item: dict) -> str:
    return f"*(Public source: {item['title']} — {item['publisher']}: {item['url']})*"


def resource_by_id(resource_id: int) -> dict | None:
    return next((item for item in load_resources() if item["id"] == resource_id), None)


def public_bundle(topic: str | None, *, fetch: bool = True, fetch_limit: int = 3) -> str:
    """Directory of relevant links plus optional fetched page text for citation."""
    resources = resources_for_topic(topic)
    if not resources:
        return ""
    parts = [format_resource_directory(resources)]
    if fetch:
        ordered = sorted(
            resources,
            key=lambda item: (
                FETCH_PRIORITY.index(item["id"]) if item["id"] in FETCH_PRIORITY else 99,
                item["id"],
            ),
        )
        urls = [item["url"] for item in ordered[:fetch_limit]]
        labels = {item["url"]: f"#{item['id']} {item['title']} ({item['publisher']})" for item in ordered}
        pages = fetch_many(urls, limit=fetch_limit)
        parts.append(format_fetched(pages, labels=labels))
    return "\n\n".join(part for part in parts if part).strip()


def _clean_cell(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _clean_link(value: str) -> str:
    text = value.strip()
    # Support bare URLs, markdown links, and {{https://...}} wrappers.
    braced = re.search(r"\{\{(https?://[^}]+)\}\}", text)
    if braced:
        return braced.group(1).strip()
    md = re.search(r"\((https?://[^)]+)\)", text)
    if md:
        return md.group(1).strip()
    plain = re.search(r"(https?://\S+)", text)
    if plain:
        return plain.group(1).rstrip(").,]")
    return text
