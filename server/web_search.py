"""Lightweight web search for market research. Failures return empty — never invent hits."""

from __future__ import annotations

import html
import re
import urllib.error
import urllib.parse
import urllib.request

from server.web_fetch import USER_AGENT

TIMEOUT_SECONDS = 12
MAX_RESULTS = 6


def search_web(query: str, limit: int = 5) -> list[dict]:
    """
    Return up to `limit` results: {title, url, snippet}.
    Uses DuckDuckGo HTML results (no API key). Empty list on failure.
    """
    limit = max(1, min(limit, MAX_RESULTS))
    query = query.strip()
    if not query:
        return []
    url = "https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            body = response.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError, OSError):
        return []
    return _parse_ddg_html(body, limit=limit)


def _parse_ddg_html(body: str, limit: int) -> list[dict]:
    results: list[dict] = []
    # Classic DDG HTML: result__a + result__snippet
    pattern = re.compile(
        r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>'
        r'.*?(?:class="result__snippet"[^>]*>(.*?)</(?:a|td)|$)',
        re.IGNORECASE | re.DOTALL,
    )
    for match in pattern.finditer(body):
        href = html.unescape(match.group(1).strip())
        title = _strip_tags(match.group(2))
        snippet = _strip_tags(match.group(3) or "")
        resolved = _unwrap_ddg_redirect(href)
        if not resolved.startswith("http"):
            continue
        if any(r["url"] == resolved for r in results):
            continue
        results.append({"title": title or resolved, "url": resolved, "snippet": snippet})
        if len(results) >= limit:
            break
    if results:
        return results
    # Fallback: any uddg= destination links
    for match in re.finditer(r"uddg=([^&\"']+)", body):
        resolved = urllib.parse.unquote(match.group(1))
        if not resolved.startswith("http"):
            continue
        if any(r["url"] == resolved for r in results):
            continue
        results.append({"title": resolved, "url": resolved, "snippet": ""})
        if len(results) >= limit:
            break
    return results


def _unwrap_ddg_redirect(href: str) -> str:
    if "uddg=" in href:
        parsed = urllib.parse.urlparse(href)
        qs = urllib.parse.parse_qs(parsed.query)
        if "uddg" in qs and qs["uddg"]:
            return urllib.parse.unquote(qs["uddg"][0])
    if href.startswith("//"):
        return "https:" + href
    return href


def _strip_tags(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()
