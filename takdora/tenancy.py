"""Tenant-first workspace services; browser input never selects a business."""

from __future__ import annotations

from dataclasses import dataclass

import reflex as rx
from sqlmodel import select

from takdora.models import Business, BusinessMembership, OwnerAccount


class WorkspaceAccessError(ValueError):
    """Bounded not-found response that does not expose tenant existence."""


@dataclass(frozen=True)
class WorkspaceRecord:
    """Display-safe workspace representation used by guards and tests."""

    id: int
    creating_owner_id: int
    name: str
    is_active: bool = True


def require_owner(owner: OwnerAccount | None) -> OwnerAccount:
    """Reject any private workflow without a server-resolved account."""
    if owner is None or owner.id is None:
        raise WorkspaceAccessError("Workspace not found.")
    return owner


def require_business_for_owner(owner_id: int, business: WorkspaceRecord) -> WorkspaceRecord:
    """Authorize a business only through its authenticated creating owner."""
    if business.creating_owner_id != owner_id or not business.is_active:
        raise WorkspaceAccessError("Workspace not found.")
    return business


def create_workspace(owner: OwnerAccount) -> Business:
    """Create exactly one draft workspace and its owner authority record."""
    authorized_owner = require_owner(owner)
    with rx.session() as session:
        existing = session.exec(
            select(Business).where(Business.creating_owner_id == authorized_owner.id)
        ).first()
        if existing is not None:
            raise WorkspaceAccessError("This account already has a workspace.")
        business = Business(creating_owner_id=authorized_owner.id or 0)
        session.add(business)
        session.flush()
        session.add(
            BusinessMembership(business_id=business.id or 0, owner_id=authorized_owner.id or 0)
        )
        session.commit()
        session.refresh(business)
        return business


def get_workspace_for_owner(owner: OwnerAccount | None) -> Business | None:
    """Resolve the sole active workspace without accepting any client business ID."""
    authorized_owner = require_owner(owner)
    with rx.session() as session:
        business = session.exec(
            select(Business).where(
                Business.creating_owner_id == authorized_owner.id,
                Business.is_active.is_(True),
            )
        ).first()
        return business
