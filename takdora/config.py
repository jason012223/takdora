"""Typed environment configuration with no browser-visible secrets."""

from __future__ import annotations

import os
from dataclasses import dataclass


class ConfigurationError(ValueError):
    """Raised when required runtime configuration is unsafe or incomplete."""


@dataclass(frozen=True)
class Settings:
    app_env: str
    database_url: str
    api_url: str
    app_secret_key: str | None
    sentry_dsn: str | None

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    def validate(self) -> None:
        if not self.database_url:
            raise ConfigurationError("DATABASE_URL must be configured.")
        if self.is_production and not self.app_secret_key:
            raise ConfigurationError("APP_SECRET_KEY must be configured in production.")
        if self.is_production and not self.api_url.startswith("https://"):
            raise ConfigurationError("API_URL must use HTTPS in production.")


def get_settings(environ: dict[str, str] | None = None) -> Settings:
    """Load configuration from an environment mapping without logging its values."""
    env = os.environ if environ is None else environ
    settings = Settings(
        app_env=env.get("APP_ENV", "development"),
        database_url=env.get(
            "DATABASE_URL", "postgresql+psycopg://takdora:takdora@db:5432/takdora"
        ),
        api_url=env.get("API_URL", "http://localhost:8000"),
        app_secret_key=env.get("APP_SECRET_KEY"),
        sentry_dsn=env.get("SENTRY_DSN"),
    )
    settings.validate()
    return settings
