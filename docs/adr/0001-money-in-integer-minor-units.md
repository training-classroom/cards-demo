# ADR 0001: Money in integer minor units

**Status:** Accepted · 2025-01-20

## Context

The card network sends amounts in minor units, and settlement reconciles to the cent. Floats and
decimal types introduced rounding differences between services.

## Decision

Every amount is an `int` in minor units: in the API (`amount_minor`), in the database, in
configuration (`CardTierPolicy`), and in calculations. `domain.money.format_minor` formats amounts for
people at the edge.

## Consequences

- No float or decimal type holds an amount (`tests/test_conventions.py`).
- Names of fields and settings that hold amounts end in `_minor`.
