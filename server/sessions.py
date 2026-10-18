"""In-memory session state. A server restart clears it."""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field


@dataclass
class Session:
    id: str
    mode: str = "chooser"
    task: str | None = None
    pitch_focus: str | None = None
    numbers_focus: str | None = None
    numbers_card: int = 0
    investor_profile: str | None = None
    topic: str | None = None
    history: list = field(default_factory=list)
    misunderstandings: list = field(default_factory=list)
    help_used: bool = False
    practice_results: list = field(default_factory=list)
    feedback_released: bool = False
    company_id: str = "tidewell-systems"
    last_calculations: list = field(default_factory=list)


class SessionStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._items: dict[str, Session] = {}

    def create(
        self,
        mode: str = "chooser",
        investor_profile: str | None = None,
        task: str | None = None,
    ) -> Session:
        session = Session(
            id=uuid.uuid4().hex[:12],
            mode=mode,
            task=task,
            investor_profile=investor_profile,
        )
        with self._lock:
            self._items[session.id] = session
        return session

    def get(self, session_id: str) -> Session | None:
        with self._lock:
            return self._items.get(session_id)


STORE = SessionStore()
