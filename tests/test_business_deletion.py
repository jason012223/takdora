"""Tests for deliberate workspace deactivation and scheduled deletion."""

from __future__ import annotations

from datetime import timedelta

import pytest

from takdora.tenancy import WorkspaceAccessError, WorkspaceRecord, schedule_workspace_deletion


def test_deletion_requires_owner_confirmation_and_deactivates_immediately() -> None:
    workspace = WorkspaceRecord(id=9, creating_owner_id=1, name="Sample")
    with pytest.raises(WorkspaceAccessError, match="confirmation"):
        schedule_workspace_deletion(1, workspace, confirmed=False)

    deletion = schedule_workspace_deletion(1, workspace, confirmed=True)
    assert deletion.is_active is False
    assert deletion.purge_after == deletion.requested_at + timedelta(days=30)


def test_unrelated_owner_cannot_schedule_deletion() -> None:
    workspace = WorkspaceRecord(id=9, creating_owner_id=1, name="Sample")
    with pytest.raises(WorkspaceAccessError, match="not found"):
        schedule_workspace_deletion(2, workspace, confirmed=True)
