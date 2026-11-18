"""Money helpers.

Amounts are integers in minor units everywhere (see docs/adr/0001-money-in-integer-minor-units.md).
This module only formats amounts for people to read.
"""

_MINOR_DIGITS = 2


def format_minor(amount_minor: int, currency: str) -> str:
    """Format an amount for messages, e.g. `format_minor(100000, "USD")` -> `"1,000.00 USD"`."""
    sign = "-" if amount_minor < 0 else ""
    major, minor = divmod(abs(amount_minor), 10**_MINOR_DIGITS)
    return f"{sign}{major:,}.{minor:0{_MINOR_DIGITS}d} {currency}"
