"""Server-side Claude call. The API key never leaves this process."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"
DEFAULT_MODEL = "claude-sonnet-5-5"
DEFAULT_MAX_TOKENS = 4096
DEFAULT_EFFORT = "low"
TIMEOUT_SECONDS = 90


class MissingCredentials(RuntimeError):
    pass


class ProviderTimeout(RuntimeError):
    pass


class ProviderError(RuntimeError):
    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


def configured() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY", "").strip())


def model_name() -> str:
    return os.environ.get("VICTORIA_MODEL", "").strip() or DEFAULT_MODEL


def effort_level() -> str:
    return os.environ.get("VICTORIA_EFFORT", "").strip() or DEFAULT_EFFORT


def complete(system: str, messages: list[dict], max_tokens: int | None = None) -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        raise MissingCredentials("ANTHROPIC_API_KEY is not set")
    token_budget = max_tokens if max_tokens is not None else DEFAULT_MAX_TOKENS
    payload = {
        "model": model_name(),
        "max_tokens": token_budget,
        "system": system,
        "messages": messages,
        # Sonnet 5.5 adaptive thinking shares this budget. Keep effort low so
        # coaching replies still have room for visible text.
        "output_config": {"effort": effort_level()},
    }
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": key,
            "anthropic-version": API_VERSION,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:500]
        raise ProviderError(f"Claude returned HTTP {error.code}: {detail}", error.code) from error
    except TimeoutError as error:
        raise ProviderTimeout(f"Claude did not respond within {TIMEOUT_SECONDS} seconds") from error
    except urllib.error.URLError as error:
        reason = getattr(error, "reason", error)
        if isinstance(reason, TimeoutError):
            raise ProviderTimeout(f"Claude did not respond within {TIMEOUT_SECONDS} seconds") from error
        raise ProviderError(f"Claude could not be reached: {reason}") from error

    text = _extract_text(body)
    if text:
        return text

    # One retry with a larger budget if thinking ate the first reply.
    if body.get("stop_reason") == "max_tokens" and token_budget < 8192:
        return complete(system, messages, max_tokens=8192)

    types = [block.get("type") for block in body.get("content", [])]
    raise ProviderError(
        "Claude returned an empty response"
        + (f" (stop_reason={body.get('stop_reason')}, content={types})" if types else "")
    )


def _extract_text(body: dict) -> str:
    parts = []
    for block in body.get("content", []):
        if block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "\n".join(part for part in parts if part).strip()
