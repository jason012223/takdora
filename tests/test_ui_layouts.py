"""Regression checks for semantic responsive layout and interaction factories."""

import inspect

from takdora.pages.ui_preview import ui_preview
from takdora.ui import layouts, primitives


def test_layouts_expose_labelled_navigation_and_mobile_menu() -> None:
    source = inspect.getsource(layouts)
    assert "Public navigation" in source
    assert "Owner navigation" in source
    assert "Marketing navigation" in source
    assert 'display={"base": "inline-flex", "md": "none"}' in source


def test_preview_composes_shared_workflow_without_private_data() -> None:
    source = inspect.getsource(ui_preview)
    assert "public_layout" in source
    assert "owner_layout" in source
    assert "marketing_layout" in source
    assert "customer information" in source


def test_dialog_and_calendar_are_reusable_and_privacy_safe() -> None:
    source = inspect.getsource(primitives)
    assert "rx.dialog.root" in source
    assert "rx.dialog.title" in source
    assert "Customer details are never shown" in source
