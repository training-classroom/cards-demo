from fastapi import APIRouter, status

from cards.api.deps import ActorDep, CardServiceDep, SessionDep
from cards.models import Authorization
from cards.repositories import authorizations as authorizations_repo
from cards.repositories import cards as cards_repo
from cards.schemas import AuthorizationCreate, AuthorizationOut, CardOut
from cards.services.authorization_rules import DECLINE_REASONS
from cards.services.card_service import AuthorizationRequest

router = APIRouter(prefix="/cards", tags=["cards"])


@router.get("", response_model=list[CardOut])
def list_cards(session: SessionDep) -> list[CardOut]:
    return [CardOut.model_validate(card) for card in cards_repo.list_all(session)]


@router.get("/{card_id}", response_model=CardOut)
def get_card(card_id: str, service: CardServiceDep) -> CardOut:
    return CardOut.model_validate(service.get(card_id))


@router.post(
    "/{card_id}/authorizations",
    status_code=status.HTTP_200_OK,
    response_model=AuthorizationOut,
    responses={200: {"description": "The decision: approved, or declined with a decline code"}},
)
def authorize(
    card_id: str, body: AuthorizationCreate, service: CardServiceDep, actor: ActorDep
) -> AuthorizationOut:
    authorization = service.authorize(
        card_id,
        AuthorizationRequest(
            merchant_name=body.merchant_name,
            merchant_category=body.merchant_category,
            amount_minor=body.amount_minor,
            currency=body.currency,
        ),
        actor=actor,
    )
    return _authorization_out(authorization)


@router.get("/{card_id}/authorizations", response_model=list[AuthorizationOut])
def list_authorizations(
    card_id: str, service: CardServiceDep, session: SessionDep
) -> list[AuthorizationOut]:
    service.get(card_id)
    return [_authorization_out(a) for a in authorizations_repo.list_for_card(session, card_id)]


@router.post("/{card_id}/close", response_model=CardOut)
def close_card(card_id: str, service: CardServiceDep, actor: ActorDep) -> CardOut:
    return CardOut.model_validate(service.close(card_id, actor=actor))


def _authorization_out(authorization: Authorization) -> AuthorizationOut:
    out = AuthorizationOut.model_validate(authorization)
    if authorization.decline_code is not None:
        out.decline_reason = DECLINE_REASONS[authorization.decline_code]
    return out
