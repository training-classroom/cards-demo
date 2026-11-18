"""Service settings, read from environment variables prefixed with `CARDS_`.

`CARDS_TIERS` replaces the whole tier table, so it must be a JSON object with every tier.
"""

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CardTierPolicy(BaseModel):
    """Limits for every card on one tier. Amounts are minor units (cents)."""

    max_authorization_minor: int = Field(gt=0, description="Largest single authorization.")


def default_tiers() -> dict[str, CardTierPolicy]:
    return {
        "classic": CardTierPolicy(max_authorization_minor=100_000),
        "gold": CardTierPolicy(max_authorization_minor=500_000),
        "corporate": CardTierPolicy(max_authorization_minor=2_500_000),
    }


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CARDS_")

    database_url: str = "sqlite:///./cards.db"
    seed_on_startup: bool = True
    tiers: dict[str, CardTierPolicy] = Field(default_factory=default_tiers)
    # Merchant category codes (MCC) no card may be used at.
    blocked_merchant_categories: frozenset[str] = frozenset({"7995"})

    def policy_for(self, tier: str) -> CardTierPolicy:
        try:
            return self.tiers[tier]
        except KeyError as exc:
            raise LookupError(f"No tier policy is configured for tier {tier!r}") from exc
