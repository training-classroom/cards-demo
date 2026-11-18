"""Shared fixtures: an in-memory database seeded with the synthetic cards, and a FrozenClock."""

from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from cards.config import Settings
from cards.main import create_app
from cards.services.card_service import CardService
from tests.support import FrozenClock


@pytest.fixture
def clock() -> FrozenClock:
    return FrozenClock(datetime(2026, 4, 7, 11, 15, tzinfo=UTC))


@pytest.fixture
def settings() -> Settings:
    return Settings(database_url="sqlite://", seed_on_startup=True)


@pytest.fixture
def app(settings: Settings, clock: FrozenClock) -> FastAPI:
    return create_app(settings, clock)


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def session(client: TestClient, app: FastAPI) -> Iterator[Session]:
    with app.state.session_factory() as db_session:
        yield db_session


@pytest.fixture
def service(session: Session, settings: Settings, clock: FrozenClock) -> CardService:
    return CardService(session, settings, clock)
