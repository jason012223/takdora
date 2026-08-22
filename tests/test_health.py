"""Health endpoint behavior must stay bounded and avoid exception disclosure."""

from unittest.mock import MagicMock, patch

from sqlalchemy.exc import OperationalError

from takdora.config import get_settings
from takdora.takdora import health_response


def test_healthz_returns_machine_readable_success_when_database_is_reachable() -> None:
    session = MagicMock()
    session.__enter__.return_value = session
    with patch("takdora.takdora.rx.session", return_value=session):
        response = health_response()
    assert response.status_code == 200
    assert response.body == b'{"status":"ok"}'


def test_healthz_returns_unavailable_without_exception_details() -> None:
    session = MagicMock()
    session.__enter__.side_effect = OperationalError("SELECT 1", {}, Exception("offline"))
    with patch("takdora.takdora.rx.session", return_value=session):
        response = health_response()
    assert response.status_code == 503
    assert response.body == b'{"status":"unavailable"}'


def test_sentry_is_opt_in_and_never_enables_default_pii_collection() -> None:
    settings = get_settings(
        {
            "APP_ENV": "production",
            "DATABASE_URL": "postgresql+psycopg://user:password@db/takdora",
            "API_URL": "https://takdora.example/api",
            "APP_SECRET_KEY": "test-secret",
            "SENTRY_DSN": "https://public@example.ingest.sentry.io/1",
            "APP_RELEASE": "test-release",
        }
    )
    with patch("sentry_sdk.init") as initialize:
        settings.initialize_sentry()
    initialize.assert_called_once_with(
        dsn="https://public@example.ingest.sentry.io/1",
        environment="production",
        release="test-release",
        send_default_pii=False,
        traces_sample_rate=0.0,
    )
