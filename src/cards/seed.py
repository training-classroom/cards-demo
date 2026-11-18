"""Synthetic seed data for local runs and tests.

Every name, token, and reference here is invented. The service never holds full card numbers, and
no real customer data may appear in this repository, in tests, or in prompts.
"""

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from cards.models import Card

ISSUED_AT = datetime(2025, 2, 3, 10, 0, tzinfo=UTC)
CLOSED_AT = datetime(2025, 8, 19, 16, 45, tzinfo=UTC)

# Card number n has id CRD-200n, account ACC-550n, token tok_syn_000n, and last4 000n.
SEED_CARDS: tuple[dict[str, str], ...] = (
    {"holder": "Synthetic Holder 01", "currency": "USD", "tier": "classic", "status": "active"},
    {"holder": "Synthetic Holder 02", "currency": "USD", "tier": "gold", "status": "active"},
    {"holder": "Synthetic Company 03", "currency": "USD", "tier": "corporate", "status": "active"},
    {"holder": "Synthetic Holder 04", "currency": "EUR", "tier": "classic", "status": "active"},
    {"holder": "Synthetic Holder 05", "currency": "USD", "tier": "classic", "status": "closed"},
)


def seed(session: Session) -> None:
    """Insert the seed cards into an empty database."""
    if session.scalar(select(func.count()).select_from(Card)):
        return
    for number, spec in enumerate(SEED_CARDS, start=1):
        session.add(
            Card(
                id=f"CRD-200{number}",
                account_ref=f"ACC-550{number}",
                cardholder_name=spec["holder"],
                token=f"tok_syn_000{number}",
                last4=f"000{number}",
                currency=spec["currency"],
                tier=spec["tier"],
                status=spec["status"],
                issued_at=ISSUED_AT,
                closed_at=CLOSED_AT if spec["status"] == "closed" else None,
            )
        )
    session.commit()
