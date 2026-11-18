# Cards Service Architecture

The Cards service manages the bank's debit cards and decides card authorizations. The card network
gateway calls it for every purchase; it answers approved or declined within the gateway's timeout and
records an audit event. It runs as one FastAPI process with a relational database (SQLite locally and
in tests).

## Layers

```
api/            HTTP: routers, request/response schemas, problem+json errors
  └── services/ business logic: authorization rules, card lifecycle, audit events
        └── repositories/   data access: queries and inserts, no rules
              └── models.py SQLAlchemy tables
```

- **`api/`** turns HTTP into service calls. It holds no rules.
- **`services/card_service.py`** owns the transaction for every change: authorizations and closing a
  card.
- **`services/authorization_rules.py`** holds the authorization rules as small functions.
- **`config.py`** reads `CARDS_*` environment variables, including the per-tier `CardTierPolicy` and
  the blocked merchant categories.
- **`clock.py`** is the only source of the current time (ADR 0004).

## Cards

A card has an id, the core-banking account it draws on (`account_ref`), a vault `token`, the last
four digits for display, a currency, a tier (`classic`, `gold`, `corporate`), and a status (`active`
or `closed`). The service never stores or returns a full card number, and the API never returns the
token.

Closing a card (`POST /cards/{id}/close`) is final. Closing a closed card is a 409.

## Authorizing a purchase

`POST /cards/{id}/authorizations` with the merchant name, merchant category code (MCC), amount, and
currency:

1. The router validates the body and calls `CardService.authorize`.
2. The service loads the card and its tier's `CardTierPolicy` and builds an `AuthorizationContext`.
3. `authorization_rules.first_decline` runs `DEFAULT_RULES` in order; the first decline code wins.
4. Only approved authorizations are stored; a declined request is answered and then discarded.
5. An audit event (`authorization.approved` or `authorization.declined`) is added, and the
   transaction commits.

The response is **200** either way, with `approved` and, for a decline, `decline_code` and
`decline_reason`. A decline is a business outcome the gateway expects, not an error.

| Order | Rule | Decline code |
|---|---|---|
| 1 | The card isn't closed | `card_closed` |
| 2 | The purchase is in the card's currency | `currency_not_supported` |
| 3 | The amount is at most the tier's `max_authorization_minor` | `over_authorization_cap` |
| 4 | The merchant category isn't blocked | `merchant_category_blocked` |

Decline codes are part of the gateway contract: new codes may be added, existing ones never renamed.

## Errors

Errors are `application/problem+json` (ADR 0002): 400 for malformed requests, 404 for unknown cards,
409 when the card's state doesn't allow the change.

## Audit

Every state change and every authorization decision records an audit event in the same transaction
(ADR 0003). `GET /audit-events` lists them.

## Testing

Tests use an in-memory database seeded with the synthetic cards in `seed.py`, and a `FrozenClock`.

## Decisions

See [`docs/adr/`](adr/).
