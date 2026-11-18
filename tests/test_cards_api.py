from datetime import timedelta

from fastapi.testclient import TestClient

from tests.support import FrozenClock, authorization_body


def authorize(client: TestClient, card_id: str = "CRD-2001", **overrides: object):
    return client.post(
        f"/cards/{card_id}/authorizations",
        json=authorization_body(**overrides),
        headers={"X-Actor": "network-gateway"},
    )


def test_list_cards_shows_last4_and_no_token(client: TestClient) -> None:
    cards = client.get("/cards").json()

    assert [c["id"] for c in cards] == ["CRD-2001", "CRD-2002", "CRD-2003", "CRD-2004", "CRD-2005"]
    assert cards[0]["last4"] == "0001"
    assert "token" not in cards[0]


def test_an_approval_is_200(client: TestClient) -> None:
    response = authorize(client)

    assert response.status_code == 200
    assert response.json()["approved"] is True
    assert response.json()["decline_code"] is None


def test_a_decline_is_also_200(client: TestClient) -> None:
    response = authorize(client, merchant_category="7995")

    assert response.status_code == 200
    body = response.json()
    assert body["approved"] is False
    assert body["decline_code"] == "merchant_category_blocked"
    assert body["decline_reason"] == "Cards can't be used at this type of merchant."


def test_declines_are_listed_with_approvals(client: TestClient, clock: FrozenClock) -> None:
    authorize(client)
    clock.advance(timedelta(minutes=5))
    authorize(client, amount_minor=999_999)

    listed = client.get("/cards/CRD-2001/authorizations").json()

    assert [a["approved"] for a in listed] == [True, False]


def test_close_then_authorize_is_declined(client: TestClient) -> None:
    closed = client.post("/cards/CRD-2002/close", headers={"X-Actor": "agent-31"})

    assert closed.status_code == 200
    assert closed.json()["status"] == "closed"
    assert authorize(client, "CRD-2002").json()["decline_code"] == "card_closed"


def test_closing_a_closed_card_is_a_409_problem(client: TestClient) -> None:
    response = client.post("/cards/CRD-2005/close")

    assert response.status_code == 409
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["type"] == "https://problems.cards.example/card-already-closed"


def test_an_invalid_body_is_a_400(client: TestClient) -> None:
    response = authorize(client, merchant_category="GROCERY")

    assert response.status_code == 400
    assert response.json()["code"] == "validation_error"


def test_an_unknown_card_is_a_404(client: TestClient) -> None:
    assert authorize(client, "CRD-0000").status_code == 404


def test_audit_events_are_listed_in_order(client: TestClient) -> None:
    authorize(client)
    client.post("/cards/CRD-2001/close", headers={"X-Actor": "agent-31"})

    events = client.get("/audit-events").json()

    assert [e["action"] for e in events] == ["authorization.approved", "card.closed"]
    assert events[1]["occurred_at"] == "2026-04-07T11:15:00Z"
