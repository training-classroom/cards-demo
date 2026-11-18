"""The rules an authorization request must pass to be approved.

Each rule takes an `AuthorizationContext` and returns a decline code, or `None` when the request
passes. `DEFAULT_RULES` runs in order and the first decline wins. Decline codes are part of the
contract with the card network gateway: add codes, never rename them.
"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from cards.config import CardTierPolicy
from cards.models import Card

DECLINE_REASONS: dict[str, str] = {
    "card_closed": "The card is closed.",
    "currency_not_supported": "The card can't be used in this currency.",
    "over_authorization_cap": "The amount is over the card's single-authorization cap.",
    "merchant_category_blocked": "Cards can't be used at this type of merchant.",
}


@dataclass(frozen=True)
class AuthorizationContext:
    card: Card
    amount_minor: int
    currency: str
    merchant_category: str
    policy: CardTierPolicy
    blocked_merchant_categories: frozenset[str]


Rule = Callable[[AuthorizationContext], str | None]


def card_must_be_open(ctx: AuthorizationContext) -> str | None:
    return "card_closed" if ctx.card.status == "closed" else None


def currency_must_match(ctx: AuthorizationContext) -> str | None:
    return "currency_not_supported" if ctx.currency != ctx.card.currency else None


def amount_within_cap(ctx: AuthorizationContext) -> str | None:
    if ctx.amount_minor > ctx.policy.max_authorization_minor:
        return "over_authorization_cap"
    return None


def merchant_category_allowed(ctx: AuthorizationContext) -> str | None:
    if ctx.merchant_category in ctx.blocked_merchant_categories:
        return "merchant_category_blocked"
    return None


DEFAULT_RULES: tuple[Rule, ...] = (
    card_must_be_open,
    currency_must_match,
    amount_within_cap,
    merchant_category_allowed,
)


def first_decline(ctx: AuthorizationContext, rules: Sequence[Rule] = DEFAULT_RULES) -> str | None:
    for rule in rules:
        code = rule(ctx)
        if code is not None:
            return code
    return None
