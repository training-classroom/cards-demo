"""Application factory. Run locally with `uv run fastapi dev src/cards/main.py`."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from cards.api import audit_events, cards, health
from cards.api.errors import install_error_handlers
from cards.clock import Clock, SystemClock
from cards.config import Settings
from cards.db import Base, make_engine, make_session_factory
from cards.seed import seed


def create_app(settings: Settings | None = None, clock: Clock | None = None) -> FastAPI:
    settings = settings or Settings()
    engine = make_engine(settings.database_url)
    session_factory = make_session_factory(engine)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        Base.metadata.create_all(engine)
        if settings.seed_on_startup:
            with session_factory() as session:
                seed(session)
        yield
        engine.dispose()

    app = FastAPI(title="Cards Service", version="2.1.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.session_factory = session_factory
    app.state.clock = clock or SystemClock()

    install_error_handlers(app)
    app.include_router(health.router)
    app.include_router(cards.router)
    app.include_router(audit_events.router)
    return app


app = create_app()
