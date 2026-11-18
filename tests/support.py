"""Test helpers shared by the test modules."""

from datetime import datetime, timedelta
from typing import Any


class FrozenClock:
    """A clock that only moves when a test moves it."""

    def __init__(self, at: datetime) -> None:
        if at.tzinfo is None:
            raise ValueError("FrozenClock needs a timezone-aware datetime")
        self._now = at

    def now(self) -> datetime:
        return self._now

    def advance(self, delta: timedelta) -> None:
        self._now += delta


def authorization_body(**overrides: Any) -> dict[str, Any]:
    """A grocery purchase of 42.50 USD, approvable on any open USD card."""
    body: dict[str, Any] = {
        "merchant_name": "Synthetic Grocer",
        "merchant_category": "5411",
        "amount_minor": 4_250,
        "currency": "USD",
    }
    body.update(overrides)
    return body
