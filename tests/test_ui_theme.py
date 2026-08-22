"""Regression coverage for the Takdora application shell."""

import inspect
from pathlib import Path

from takdora import takdora
from takdora.ui import shell, theme


def test_root_uses_the_shared_semantic_shell_and_readiness_control() -> None:
    source = inspect.getsource(takdora.index)
    assert "application_shell" in source
    assert "readiness-control" in source
    assert "main" in inspect.getsource(shell.application_shell)


def test_theme_exports_semantic_tokens_without_browser_data() -> None:
    assert theme.TOKENS["foreground"]
    assert theme.TOKENS["focus"]
    assert theme.takdora_theme is not None


def test_app_loads_the_local_semantic_stylesheet() -> None:
    source = inspect.getsource(takdora)
    stylesheet = Path(__file__).parents[1] / "assets" / "takdora.css"
    assert "takdora.css" in source
    assert "prefers-reduced-motion" in stylesheet.read_text(encoding="utf-8")


def test_readiness_event_remains_server_side_and_argument_free() -> None:
    handler = takdora.FoundationState.__dict__["run_readiness_probe"]
    assert list(inspect.signature(handler.fn).parameters) == ["self"]
