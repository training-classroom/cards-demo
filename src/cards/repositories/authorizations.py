from sqlalchemy import select
from sqlalchemy.orm import Session

from cards.models import Authorization


def list_for_card(session: Session, card_id: str) -> list[Authorization]:
    query = (
        select(Authorization)
        .where(Authorization.card_id == card_id)
        .order_by(Authorization.created_at, Authorization.id)
    )
    return list(session.scalars(query))
