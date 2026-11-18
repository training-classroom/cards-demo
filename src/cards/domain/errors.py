"""Errors the service layer raises. The API maps each to a problem+json response
(see docs/adr/0002-problem-details-for-errors.md). A declined authorization is not an error."""


class CardsError(Exception):
    status: int = 400
    code: str = "bad_request"
    title: str = "Bad request"

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class CardNotFound(CardsError):
    status = 404
    code = "card_not_found"
    title = "Card not found"


class CardStateConflict(CardsError):
    """The card is in a state that doesn't allow the requested change."""

    status = 409

    def __init__(self, code: str, title: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.title = title
