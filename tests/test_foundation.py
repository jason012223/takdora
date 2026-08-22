"""Focused tests for the safe Reflex/PostgreSQL readiness tracer."""

import inspect
from unittest.mock import MagicMock, patch

from takdora.models import record_probe
from takdora.takdora import FoundationState


def test_record_probe_persists_and_returns_a_non_sensitive_row() -> None:
    session = MagicMock()
    session.__enter__.return_value = session
    session.refresh.side_effect = lambda probe: setattr(probe, "id", 7)
    with patch("takdora.models.rx.session", return_value=session):
        result = record_probe()
    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once()
    assert result.id == 7


def test_readiness_event_never_accepts_browser_persistence_data() -> None:
    handler = FoundationState.__dict__["run_readiness_probe"]
    assert list(inspect.signature(handler.fn).parameters) == ["self"]
