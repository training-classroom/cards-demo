"""Card lifecycle and authorization decisions."""

import uuid
from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy.orm import Session

from cards import audit
from cards.clock import Clock
from cards.config import Settings
from cards.domain.errors import CardNotFound, CardStateConflict
from cards.models import Authorization, Card
from cards.repositories import cards as cards_repo
from cards.services.authorization_rules import (
    DEFAULT_RULES,
    AuthorizationContext,
    Rule,
    first_decline,
)


@dataclass(frozen=True)
class AuthorizationRequest:
    merchant_name: str
    merchant_category: str
    amount_minor: int
    currency: str


def new_authorization_id() -> str:
    return f"AUTH-{uuid.uuid4().hex[:16].upper()}"


class CardService:
    def __init__(
        self,
        session: Session,
        settings: Settings,
        clock: Clock,
        rules: Sequence[Rule] = DEFAULT_RULES,
    ) -> None:
        self._session = session
        self._settings = settings
        self._clock = clock
        self._rules = rules

    def get(self, card_id: str) -> Card:
        card = cards_repo.get(self._session, card_id)
        if card is None:
            raise CardNotFound(f"No card with id {card_id}.")
        return card

    def authorize(
        self, card_id: str, request: AuthorizationRequest, *, actor: str
    ) -> Authorization:
        """Decide an authorization request. A decline is a normal outcome, stored and audited."""
        card = self.get(card_id)
        context = AuthorizationContext(
            card=card,
            amount_minor=request.amount_minor,
            currency=request.currency,
            merchant_category=request.merchant_category,
            policy=self._settings.policy_for(card.tier),
            blocked_merchant_categories=self._settings.blocked_merchant_categories,
        )
        decline_code = first_decline(context, self._rules)
        now = self._clock.now()
        authorization = Authorization(
            id=new_authorization_id(),
            card_id=card.id,
            merchant_name=request.merchant_name,
            merchant_category=request.merchant_category,
            amount_minor=request.amount_minor,
            currency=request.currency,
            approved=decline_code is None,
            decline_code=decline_code,
            created_at=now,
        )
        self._session.add(authorization)
        audit.record(
            self._session,
            occurred_at=now,
            actor=actor,
            action="authorization.approved" if decline_code is None else "authorization.declined",
            entity_type="authorization",
            entity_id=authorization.id,
            details={"card_id": card.id, "decline_code": decline_code},
        )
        self._session.commit()
        return authorization

    def close(self, card_id: str, *, actor: str) -> Card:
        card = self.get(card_id)
        if card.status == "closed":
            raise CardStateConflict(
                "card_already_closed", "Card already closed", f"Card {card.id} is already closed."
            )
        now = self._clock.now()
        card.status = "closed"
        card.closed_at = now
        audit.record(
            self._session,
            occurred_at=now,
            actor=actor,
            action="card.closed",
            entity_type="card",
            entity_id=card.id,
        )
        self._session.commit()
        return card
