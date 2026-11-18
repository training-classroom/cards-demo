"""Problem details (RFC 9457) for every error response (docs/adr/0002).

Status codes: 400 malformed request, 404 unknown card, 409 the card's state doesn't allow the
change. A declined authorization is a 200 response, not an error.
"""

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from cards.domain.errors import CardsError

PROBLEM_TYPE_BASE = "https://problems.cards.example/"
PROBLEM_MEDIA_TYPE = "application/problem+json"


def problem_response(
    *, status: int, code: str, title: str, detail: str, **extensions: Any
) -> JSONResponse:
    body = {
        "type": PROBLEM_TYPE_BASE + code.replace("_", "-"),
        "title": title,
        "status": status,
        "detail": detail,
        "code": code,
        **extensions,
    }
    return JSONResponse(body, status_code=status, media_type=PROBLEM_MEDIA_TYPE)


async def _cards_error(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, CardsError)
    return problem_response(status=exc.status, code=exc.code, title=exc.title, detail=exc.detail)


async def _validation_error(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    errors = [{"location": list(e["loc"]), "message": e["msg"]} for e in exc.errors()]
    return problem_response(
        status=400,
        code="validation_error",
        title="Invalid request",
        detail="The request body or headers failed validation.",
        errors=errors,
    )


async def _http_error(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, StarletteHTTPException)
    code = "not_found" if exc.status_code == 404 else "http_error"
    return problem_response(
        status=exc.status_code, code=code, title=str(exc.detail), detail=str(exc.detail)
    )


def install_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(CardsError, _cards_error)
    app.add_exception_handler(RequestValidationError, _validation_error)
    app.add_exception_handler(StarletteHTTPException, _http_error)
