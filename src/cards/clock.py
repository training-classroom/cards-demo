"""The service's source of the current time.

Every timestamp the service records comes from a `Clock` (see docs/adr/0004-injected-utc-clock.md).
Nothing else calls `datetime.now()`, so tests can pin time and every timestamp is aware UTC.
"""

from datetime import UTC, datetime
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime:
        """Return the current time as a timezone-aware UTC datetime."""
        ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)
