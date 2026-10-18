"""Local HTTP API for Victoria. Bind to localhost only."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from server import claude_client
from server.agent import opening, respond
from server.audit_review import apply_audit_fixes, review_pitch_and_deck
from server.deck_draft import deck_draft_pack
from server.finance import export_income_statement
from server.materials import investor_profiles
from server.paths import INCOME_CSV, ROOT
from server.sessions import STORE

STATIC = Path(__file__).resolve().parent / "static"


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def ensure_data() -> None:
    if not INCOME_CSV.exists():
        export_income_statement()


class Handler(BaseHTTPRequestHandler):
    server_version = "Victoria/0.1"

    def log_message(self, fmt: str, *args) -> None:
        print(f"[victoria] {self.address_string()} {fmt % args}", flush=True)

    def do_OPTIONS(self) -> None:
        self._send(204, b"", "text/plain")

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in {"/", "/index.html"}:
            self._send(200, (STATIC / "index.html").read_bytes(), "text/html; charset=utf-8")
            return
        if path in {"/health", "/api/health", "/api/meta"}:
            provider = "claude" if claude_client.configured() else "local"
            body = {
                "ok": True,
                "provider": provider,
                "model": claude_client.model_name() if provider == "claude" else None,
                "company_id": "tidewell-systems",
                "profiles": investor_profiles(),
                "persistence": "memory",
            }
            self._send_json(200, body)
            return
        if path == "/api/deck-draft":
            query = parse_qs(urlparse(self.path).query)
            template = (query.get("template") or ["seed_fix"])[0]
            pack = deck_draft_pack(template)
            self._send_json(200, pack)
            return
        if path == "/api/audit-review":
            query = parse_qs(urlparse(self.path).query)
            template = (query.get("template") or ["seed_fix"])[0]
            search = (query.get("search") or ["1"])[0] not in {"0", "false", "no"}
            # GET audits the template only; POST with slides for the live draft.
            self._send_json(200, review_pitch_and_deck(template, search=search))
            return
        if path.startswith("/api/sessions/"):
            session_id = path.removeprefix("/api/sessions/").strip("/")
            session = STORE.get(session_id)
            if session is None:
                self._send_json(404, {"error": "session not found"})
                return
            self._send_json(
                200,
                {
                    "session_id": session.id,
                    "mode": session.mode,
                    "task": session.task,
                    "investor_profile": session.investor_profile,
                    "topic": session.topic,
                    "help_used": session.help_used,
                    "misunderstandings": session.misunderstandings,
                    "practice_results": session.practice_results,
                    "history": session.history,
                },
            )
            return
        self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            payload = self._read_json()
        except ValueError as error:
            self._send_json(400, {"error": str(error)})
            return
        try:
            if path == "/api/sessions":
                # Sessions start at the task menu. Mode/profile may still be
                # supplied for tests or older clients.
                mode = payload.get("mode") or "chooser"
                if mode not in {"chooser", "coaching", "investor"}:
                    raise ValueError("mode must be chooser, coaching, or investor")
                profile = payload.get("investor_profile")
                if profile:
                    known = {item["id"] for item in investor_profiles()}
                    if profile not in known:
                        raise ValueError("unknown investor profile")
                if mode == "chooser":
                    profile = None
                elif mode == "coaching":
                    profile = None
                elif mode == "investor" and not profile:
                    profile = "the-lead-seed-fund"
                session = STORE.create(mode, profile if mode == "investor" else None)
                self._send_json(201, opening(session))
                return
            if path == "/api/audit-review":
                template = str(payload.get("template") or "seed_fix")
                search = payload.get("search", True)
                if isinstance(search, str):
                    search = search.lower() not in {"0", "false", "no"}
                slides = payload.get("slides")
                if slides is not None and not isinstance(slides, list):
                    raise ValueError("slides must be a list")
                resolved = payload.get("resolved_keys") or []
                if not isinstance(resolved, list):
                    raise ValueError("resolved_keys must be a list")
                self._send_json(
                    200,
                    review_pitch_and_deck(
                        template,
                        search=bool(search),
                        slides=slides,
                        resolved_keys=[str(k) for k in resolved],
                    ),
                )
                return
            if path == "/api/audit-review/apply":
                template = str(payload.get("template") or "seed_fix")
                search = payload.get("search", True)
                if isinstance(search, str):
                    search = search.lower() not in {"0", "false", "no"}
                slides = payload.get("slides")
                if slides is not None and not isinstance(slides, list):
                    raise ValueError("slides must be a list")
                resolved = payload.get("resolved_keys") or []
                if not isinstance(resolved, list):
                    raise ValueError("resolved_keys must be a list")
                self._send_json(
                    200,
                    apply_audit_fixes(
                        template,
                        search=bool(search),
                        slides=slides,
                        resolved_keys=[str(k) for k in resolved],
                    ),
                )
                return
            if path.startswith("/api/sessions/") and path.endswith("/messages"):
                session_id = path.removeprefix("/api/sessions/").removesuffix("/messages").strip("/")
                session = STORE.get(session_id)
                if session is None:
                    self._send_json(404, {"error": "session not found"})
                    return
                self._send_json(200, respond(session, str(payload.get("text", ""))))
                return
        except ValueError as error:
            self._send_json(400, {"error": str(error)})
            return
        except claude_client.ProviderTimeout as error:
            self._send_json(504, {"error": str(error), "provider": "claude"})
            return
        except claude_client.ProviderError as error:
            self._send_json(502, {"error": str(error), "provider": "claude"})
            return
        self._send_json(404, {"error": "not found"})

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError("request body must be JSON") from error
        if not isinstance(data, dict):
            raise ValueError("request body must be a JSON object")
        return data

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        if body:
            self.wfile.write(body)


def main() -> None:
    load_env(ROOT / ".env")
    ensure_data()
    port = int(os.environ.get("PORT", "8787"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    provider = "claude" if claude_client.configured() else "local"
    print(f"Victoria listening on http://127.0.0.1:{port} (provider: {provider})", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
