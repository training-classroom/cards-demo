"""FastAPI dependencies. Everything comes from `app.state`, which `create_app` fills."""

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Header, Request
from sqlalchemy.orm import Session

from cards.services.card_service import CardService


def get_session(request: Request) -> Iterator[Session]:
    session = request.app.state.session_factory()
    try:
        yield session
    finally:
        session.close()


def get_actor(x_actor: Annotated[str | None, Header(max_length=100)] = None) -> str:
    """Who is calling, for the audit trail. The API gateway sets `X-Actor` in production."""
    return x_actor or "unknown"


SessionDep = Annotated[Session, Depends(get_session)]
ActorDep = Annotated[str, Depends(get_actor)]


def get_card_service(request: Request, session: SessionDep) -> CardService:
    return CardService(session, request.app.state.settings, request.app.state.clock)


CardServiceDep = Annotated[CardService, Depends(get_card_service)]
