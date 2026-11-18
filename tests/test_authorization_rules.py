from datetime import UTC, datetime

import pytest

from cards.config import CardTierPolicy
from cards.models import Card
from cards.services.authorization_rules import (
    DECLINE_REASONS,
    DEFAULT_RULES,
    AuthorizationContext,
    first_decline,
)


def card(**overrides: str) -> Card:
    fields = {"currency": "USD", "tier": "classic", "status": "active"} | overrides
    return Card(
        id="CRD-T1",
        account_ref="ACC-T1",
        cardholder_name="Synthetic Test Holder",
        token="tok_test",
        last4="9999",
        issued_at=datetime(2025, 1, 1, tzinfo=UTC),
        **fields,
    )


def context(**overrides: object) -> AuthorizationContext:
    fields: dict[str, object] = {
        "card": card(),
        "amount_minor": 5_000,
        "currency": "USD",
        "merchant_category": "5411",
        "policy": CardTierPolicy(max_authorization_minor=10_000),
        "blocked_merchant_categories": frozenset({"7995"}),
    }
    fields.update(overrides)
    return AuthorizationContext(**fields)  # type: ignore[arg-type]


def test_an_ordinary_purchase_is_approved() -> None:
    assert first_decline(context()) is None


@pytest.mark.parametrize(
    ("overrides", "code"),
    [
        ({"card": card(status="closed")}, "card_closed"),
        ({"currency": "EUR"}, "currency_not_supported"),
        ({"amount_minor": 10_001}, "over_authorization_cap"),
        ({"merchant_category": "7995"}, "merchant_category_blocked"),
    ],
)
def test_each_rule_declines_its_case(overrides: dict[str, object], code: str) -> None:
    assert first_decline(context(**overrides)) == code


def test_the_cap_is_inclusive() -> None:
    assert first_decline(context(amount_minor=10_000)) is None


def test_every_decline_code_has_a_reason() -> None:
    assert len(DEFAULT_RULES) == len(DECLINE_REASONS)
