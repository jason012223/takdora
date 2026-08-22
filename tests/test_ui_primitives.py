"""Focused assertions for Takdora UI factories and its synthetic gallery."""

import inspect

from takdora.pages import design_system
from takdora.ui import primitives


def test_primitives_require_semantic_labels_and_feedback() -> None:
    source = inspect.getsource(primitives)
    assert "html_for=field_id" in source
    assert "aria_invalid" in source
    assert 'role="alert"' in source
    assert "column_header_cell" in source


def test_gallery_uses_exported_primitives_and_labels_demo_data() -> None:
    source = inspect.getsource(design_system.design_system)
    assert "field(" in source
    assert "feedback(" in source
    assert "synthetic demo data" in source
