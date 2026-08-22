"""Regression tests for owner-scoped workspaces."""

from __future__ import annotations

import pytest

from takdora.tenancy import WorkspaceAccessError, WorkspaceRecord, require_business_for_owner


def test_workspace_access_is_derived_from_the_authenticated_owner() -> None:
    workspace = WorkspaceRecord(id=8, creating_owner_id=1, name="Sample business")
    assert require_business_for_owner(1, workspace).id == 8
    with pytest.raises(WorkspaceAccessError, match="not found"):
        require_business_for_owner(2, workspace)


def test_inactive_workspaces_are_not_returned_as_dashboard_records() -> None:
    workspace = WorkspaceRecord(id=8, creating_owner_id=1, name="Sample business", is_active=False)
    with pytest.raises(WorkspaceAccessError, match="not found"):
        require_business_for_owner(1, workspace)
