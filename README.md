# Cards Service

Debit card lifecycle and authorization decisions for the bank's card network gateway: per-tier
authorization caps, blocked merchant categories, and an audit trail of every decision and change.

## Requirements

- Python 3.14 and [uv](https://docs.astral.sh/uv/) (uv installs the Python version in
  `.python-version` when it's missing)
- Git

## Set up

```powershell
uv sync
```

## Run the tests and checks

```powershell
uv run pytest
uv run ruff check
uv run ruff format --check
uv run python scripts/check_dependencies.py
```

The same checks run in CI on every pull request (`.github/workflows/ci.yml`).

## Run the service

```powershell
uv run fastapi dev src/cards/main.py
```

The API docs are at http://127.0.0.1:8000/docs. On first start the service creates `cards.db` and
seeds it with synthetic cards (`src/cards/seed.py`). Delete the file to start over.

Authorize a purchase:

```powershell
$body = '{"merchant_name":"Synthetic Grocer","merchant_category":"5411","amount_minor":4250,"currency":"USD"}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/cards/CRD-2001/authorizations `
  -Headers @{ "X-Actor" = "network-gateway" } -ContentType "application/json" -Body $body
```

## Configuration

Settings come from environment variables prefixed with `CARDS_` (`src/cards/config.py`):

| Variable | Default |
|---|---|
| `CARDS_DATABASE_URL` | `sqlite:///./cards.db` |
| `CARDS_SEED_ON_STARTUP` | `true` |
| `CARDS_TIERS` | JSON object with every tier; defaults in `config.py` (`max_authorization_minor`: classic 100000, gold 500000, corporate 2500000) |
| `CARDS_BLOCKED_MERCHANT_CATEGORIES` | `["7995"]` |

## Project layout

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and the decisions in [docs/adr/](docs/adr/).

## Dependencies

Every direct dependency must be listed in `dependency-policy.toml` with its license and approval
reference. `scripts/check_dependencies.py` fails the build when one isn't.

## Contributing

Open a pull request against `main` using the template. Every change needs a linked change request,
tests, and an approving review.
