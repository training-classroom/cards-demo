# ADR 0004: An injected UTC clock

**Status:** Accepted · 2025-03-04

## Context

Card lifecycle timestamps and any future time-based rule must be testable, and naive datetimes mixed
with aware ones raised `TypeError` at run time.

## Decision

- `clock.Clock` is the only source of the current time. `create_app` takes a clock and services
  receive it. Production uses `SystemClock`; tests use `FrozenClock` from `tests/support.py`.
- Every datetime is timezone-aware **UTC**; `models.UTCDateTime` stores UTC and returns aware values.

## Consequences

- No code outside `clock.py` calls `datetime.now()`, `datetime.utcnow()`, `date.today()`, or
  `time.time()` (`tests/test_conventions.py`).
- Tests set the time explicitly and move it with `FrozenClock.advance`.
