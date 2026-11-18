"""Database tables.

The service never stores a full card number: a card has a `token` issued by the card vault and the
last four digits for display. Timestamps use `UTCDateTime` (stored as naive UTC, returned as aware
UTC), so nothing outside this module sees a naive datetime.
"""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.engine import Dialect
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import TypeDecorator

from cards.db import Base


class UTCDateTime(TypeDecorator[datetime]):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("Timestamps must be timezone-aware; use the injected Clock")
        return value.astimezone(UTC).replace(tzinfo=None)

    def process_result_value(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        if value is None:
            return None
        return value.replace(tzinfo=UTC)


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    # The customer's account in core banking that the card draws on.
    account_ref: Mapped[str] = mapped_column(String(20))
    cardholder_name: Mapped[str] = mapped_column(String(100))
    token: Mapped[str] = mapped_column(String(40), unique=True)
    last4: Mapped[str] = mapped_column(String(4))
    currency: Mapped[str] = mapped_column(String(3))
    tier: Mapped[str] = mapped_column(String(20))
    # active | closed
    status: Mapped[str] = mapped_column(String(20))
    issued_at: Mapped[datetime] = mapped_column(UTCDateTime)
    closed_at: Mapped[datetime | None] = mapped_column(UTCDateTime, default=None)


class Authorization(Base):
    """An authorization decision. Approved and declined requests are both stored."""

    __tablename__ = "authorizations"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    card_id: Mapped[str] = mapped_column(ForeignKey("cards.id"))
    merchant_name: Mapped[str] = mapped_column(String(100))
    merchant_category: Mapped[str] = mapped_column(String(4))
    amount_minor: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(3))
    approved: Mapped[bool] = mapped_column(Boolean)
    decline_code: Mapped[str | None] = mapped_column(String(40), default=None)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    occurred_at: Mapped[datetime] = mapped_column(UTCDateTime)
    actor: Mapped[str] = mapped_column(String(100))
    action: Mapped[str] = mapped_column(String(60))
    entity_type: Mapped[str] = mapped_column(String(40))
    entity_id: Mapped[str] = mapped_column(String(40))
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
