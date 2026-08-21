"""Focused tests for the safe Reflex/PostgreSQL readiness tracer."""

import inspect
from unittest.mock import MagicMock, patch

from takdora.models import FoundationProbe, record_probe
from takdora.takdora import FoundationState


def test_record_probe_persists_and_returns_a_non_sensitive_row() -> None:
    session = MagicMock()
    probe = FoundationProbe(id=7)
    session.__enter__.return_value = session
    with patch("takdora.models.rx.session", return_value=session):
        result = record_probe()
    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once()
    assert result.id == 7


def test_readiness_event_never_accepts_browser_persistence_data() -> None:
    assert list(inspect.signature(FoundationState.run_readiness_probe).parameters) == ["self"]
