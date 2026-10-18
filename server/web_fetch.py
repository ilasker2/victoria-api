"""Fetch public resource pages for citation. Failures are reported, never invented."""

from __future__ import annotations

import html
import re
import time
import urllib.error
import urllib.request

TIMEOUT_SECONDS = 12
MAX_CHARS = 3500
CACHE_SECONDS = 3600
USER_AGENT = "VictoriaCoach/0.1 (+local; educational founder coaching)"

_cache: dict[str, tuple[float, dict]] = {}


def fetch_text(url: str, max_chars: int = MAX_CHARS) -> dict:
    """Return {url, ok, text|error}. Results cached for CACHE_SECONDS."""
    now = time.time()
    cached = _cache.get(url)
    if cached and now - cached[0] < CACHE_SECONDS:
        return dict(cached[1])
    result = _fetch_uncached(url, max_chars=max_chars)
    _cache[url] = (now, result)
    return dict(result)


def clear_cache() -> None:
    _cache.clear()


def _fetch_uncached(url: str, max_chars: int = MAX_CHARS) -> dict:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            raw = response.read()
            charset = response.headers.get_content_charset() or "utf-8"
            body = raw.decode(charset, errors="replace")
    except urllib.error.HTTPError as error:
        return {"url": url, "ok": False, "error": f"HTTP {error.code}"}
    except Exception as error:  # noqa: BLE001 - surface any network failure cleanly
        return {"url": url, "ok": False, "error": str(error)}
    text = _html_to_text(body)
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[truncated]"
    if not text.strip():
        return {"url": url, "ok": False, "error": "empty page text"}
    return {"url": url, "ok": True, "text": text}


def fetch_many(urls: list[str], limit: int = 4) -> list[dict]:
    results = []
    for url in urls[:limit]:
        results.append(fetch_text(url))
    return results


def format_fetched(pages: list[dict], labels: dict[str, str] | None = None) -> str:
    if not pages:
        return ""
    labels = labels or {}
    chunks = ["## Fetched public pages (use only what appears here)", ""]
    for page in pages:
        title = labels.get(page["url"], page["url"])
        if page.get("ok"):
            chunks.append(f"### {title}\nURL: {page['url']}\n\n{page['text']}")
        else:
            chunks.append(
                f"### {title}\nURL: {page['url']}\n\n"
                f"[Could not fetch: {page.get('error', 'unknown error')}. "
                f"Point the founder to the link; do not invent its contents.]"
            )
        chunks.append("")
    return "\n".join(chunks)


def _html_to_text(body: str) -> str:
    cleaned = re.sub(r"(?is)<(script|style|noscript).*?>.*?</\1>", " ", body)
    cleaned = re.sub(r"(?is)<br\s*/?>", "\n", cleaned)
    cleaned = re.sub(r"(?is)</p>", "\n\n", cleaned)
    cleaned = re.sub(r"(?is)</(div|h1|h2|h3|li|tr)>", "\n", cleaned)
    cleaned = re.sub(r"(?is)<[^>]+>", " ", cleaned)
    cleaned = html.unescape(cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()
