"""Health endpoint behavior must stay bounded and avoid exception disclosure."""

from unittest.mock import MagicMock, patch

from sqlalchemy.exc import OperationalError

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
