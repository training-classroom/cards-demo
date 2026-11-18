from sqlalchemy import select
from sqlalchemy.orm import Session

from cards.models import Card


def get(session: Session, card_id: str) -> Card | None:
    return session.get(Card, card_id)


def list_all(session: Session) -> list[Card]:
    return list(session.scalars(select(Card).order_by(Card.id)))
