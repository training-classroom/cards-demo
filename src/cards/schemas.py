"""Request and response bodies. Amounts are integers in minor units."""

from datetime import datetime
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field


class AuthorizationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    merchant_name: Annotated[str, Field(min_length=1, max_length=100)]
    merchant_category: Annotated[str, Field(pattern=r"^\d{4}$", examples=["5411"])]
    amount_minor: Annotated[int, Field(gt=0)]
    currency: Annotated[str, Field(pattern=r"^[A-Z]{3}$")]


class AuthorizationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    card_id: str
    merchant_name: str
    merchant_category: str
    amount_minor: int
    currency: str
    approved: bool
    decline_code: str | None
    decline_reason: str | None = None
    created_at: datetime


class CardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    account_ref: str
    cardholder_name: str
    last4: str
    currency: str
    tier: str
    status: str
    issued_at: datetime
    closed_at: datetime | None


class AuditEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    occurred_at: datetime
    actor: str
    action: str
    entity_type: str
    entity_id: str
    details: dict[str, Any]
