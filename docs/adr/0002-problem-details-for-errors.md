# ADR 0002: Problem details for errors; declines are not errors

**Status:** Accepted · 2025-02-10

## Context

The gateway and the servicing app both call this service. They need to tell a malformed request
from an unknown card from a state conflict, and they must never treat a declined purchase as a
failure to retry.

## Decision

- Every error response is `application/problem+json` (RFC 9457) with `type`, `title`, `status`,
  `detail`, and `code`. `type` is `https://problems.cards.example/` plus the code with hyphens.
  `api/errors.py` builds every error response.
- 400 for a malformed request, 404 for an unknown card, 409 when the card's current state doesn't
  allow the requested change (for example, closing a closed card).
- An authorization decision is always **200**. A decline carries `approved: false`, a `decline_code`
  from `authorization_rules.DECLINE_REASONS`, and a `decline_reason`.

## Consequences

- A new decline reason is a new code and reason in `authorization_rules.py`; the API needs no change.
- A new state change that can conflict raises `CardStateConflict` with its own code.
