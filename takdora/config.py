"""Typed environment configuration with no browser-visible secrets."""

from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urlsplit


class ConfigurationError(ValueError):
    """Raised when required runtime configuration is unsafe or incomplete."""


@dataclass(frozen=True)
class Settings:
    app_env: str
    database_url: str
    api_url: str
    app_secret_key: str | None
    sentry_dsn: str | None
    release: str | None
    public_app_origin: str
    smtp_host: str | None
    smtp_port: int
    smtp_username: str | None
    smtp_password: str | None
    mail_from: str | None
    object_storage_endpoint_url: str | None
    object_storage_bucket: str | None
    object_storage_access_key_id: str | None
    object_storage_secret_access_key: str | None
    object_storage_region: str | None
    maintenance_mode: bool
    maintenance_contact: str | None
    synthetic_demo_enabled: bool

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
        origin = urlsplit(self.public_app_origin)
        if not origin.netloc or origin.path not in ("", "/"):
            raise ConfigurationError("PUBLIC_APP_ORIGIN must be an absolute origin without a path.")
        if self.is_production and origin.scheme != "https":
            raise ConfigurationError("PUBLIC_APP_ORIGIN must be an HTTPS origin without a path.")
        if self.is_production and (not self.smtp_host or not self.mail_from):
            raise ConfigurationError("SMTP_HOST and MAIL_FROM must be configured in production.")
        storage_values = (
            self.object_storage_endpoint_url,
            self.object_storage_bucket,
            self.object_storage_access_key_id,
            self.object_storage_secret_access_key,
            self.object_storage_region,
        )
        if any(storage_values) and not all(storage_values):
            raise ConfigurationError("All object storage settings must be configured together.")
        if self.is_production and not all(storage_values):
            raise ConfigurationError("Private object storage must be configured in production.")

    @property
    def sentry_environment(self) -> str:
        """Return a non-sensitive tag suitable for error monitoring."""
        return self.app_env

    def initialize_sentry(self) -> None:
        """Enable error monitoring only when an operator supplied a DSN.

        Customer data is intentionally not added as tags or request context.
        Sentry's default PII filtering remains enabled by explicitly opting out
        of SDK-side PII collection.
        """
        if not self.sentry_dsn:
            return

        import sentry_sdk

        sentry_sdk.init(
            dsn=self.sentry_dsn,
            environment=self.sentry_environment,
            release=self.release,
            send_default_pii=False,
            traces_sample_rate=0.0,
        )


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
        release=env.get("RENDER_GIT_COMMIT") or env.get("APP_RELEASE"),
        public_app_origin=env.get("PUBLIC_APP_ORIGIN", "https://takdora.app"),
        smtp_host=env.get("SMTP_HOST"),
        smtp_port=int(env.get("SMTP_PORT", "587")),
        smtp_username=env.get("SMTP_USERNAME"),
        smtp_password=env.get("SMTP_PASSWORD"),
        mail_from=env.get("MAIL_FROM"),
        object_storage_endpoint_url=env.get("OBJECT_STORAGE_ENDPOINT_URL"),
        object_storage_bucket=env.get("OBJECT_STORAGE_BUCKET"),
        object_storage_access_key_id=env.get("OBJECT_STORAGE_ACCESS_KEY_ID"),
        object_storage_secret_access_key=env.get("OBJECT_STORAGE_SECRET_ACCESS_KEY"),
        object_storage_region=env.get("OBJECT_STORAGE_REGION"),
        maintenance_mode=env.get("MAINTENANCE_MODE", "false").casefold() == "true",
        maintenance_contact=env.get("MAINTENANCE_CONTACT"),
        synthetic_demo_enabled=env.get("SYNTHETIC_DEMO_ENABLED", "false").casefold() == "true",
    )
    settings.validate()
    return settings
