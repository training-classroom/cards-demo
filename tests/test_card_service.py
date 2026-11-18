import pytest
from sqlalchemy.orm import Session

from cards import audit
from cards.domain.errors import CardNotFound, CardStateConflict
from cards.repositories import authorizations as authorizations_repo
from cards.services.card_service import AuthorizationRequest, CardService
from tests.support import FrozenClock


def request(**overrides: object) -> AuthorizationRequest:
    fields: dict[str, object] = {
        "merchant_name": "Synthetic Grocer",
        "merchant_category": "5411",
        "amount_minor": 4_250,
        "currency": "USD",
    }
    fields.update(overrides)
    return AuthorizationRequest(**fields)  # type: ignore[arg-type]


def test_an_approval_is_stored_and_audited(service: CardService, session: Session) -> None:
    authorization = service.authorize("CRD-2001", request(), actor="gateway")

    assert authorization.approved
    [event] = audit.list_events(session, entity_id=authorization.id)
    assert event.action == "authorization.approved"
    assert event.actor == "gateway"


def test_a_decline_is_stored_with_its_code(service: CardService, session: Session) -> None:
    authorization = service.authorize("CRD-2001", request(amount_minor=100_001), actor="gateway")

    assert not authorization.approved
    assert authorization.decline_code == "over_authorization_cap"
    stored = authorizations_repo.list_for_card(session, "CRD-2001")
    assert [a.decline_code for a in stored] == ["over_authorization_cap"]
    [event] = audit.list_events(session, entity_id=authorization.id)
    assert event.action == "authorization.declined"


def test_closing_a_card_records_when_and_who(
    service: CardService, session: Session, clock: FrozenClock
) -> None:
    card = service.close("CRD-2002", actor="agent-31")

    assert card.status == "closed"
    assert card.closed_at == clock.now()
    [event] = audit.list_events(session, entity_id="CRD-2002")
    assert (event.action, event.actor) == ("card.closed", "agent-31")


def test_a_closed_card_cant_be_closed_again(service: CardService) -> None:
    with pytest.raises(CardStateConflict) as error:
        service.close("CRD-2005", actor="agent-31")

    assert error.value.code == "card_already_closed"


def test_a_closed_card_declines_everything(service: CardService) -> None:
    assert service.authorize("CRD-2005", request(), actor="gateway").decline_code == "card_closed"


def test_an_unknown_card_is_not_found(service: CardService) -> None:
    with pytest.raises(CardNotFound):
        service.authorize("CRD-0000", request(), actor="gateway")
