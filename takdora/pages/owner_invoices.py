"""Private, concise invoice drafting and manual-payment screens."""

from __future__ import annotations

import reflex as rx

from takdora.auth import AuthenticationError, AuthState
from takdora.demo import is_synthetic_demo_owner
from takdora.invoicing import (
    BIR_BOUNDARY,
    issue_invoice,
    owner_invoice,
    owner_invoices,
    queue_invoice_email,
    set_received_total,
    update_invoice_draft,
    void_and_redraft,
)
from takdora.tenancy import WorkspaceAccessError
from takdora.pages.demo import synthetic_demo_banner
from takdora.ui.layouts import owner_layout
from takdora.ui.primitives import feedback, status_badge


class OwnerInvoicesState(AuthState):
    """Owner UI state; IDs are only ever authorized by the domain commands."""

    selected_invoice_id: str = ""
    status_filter: str = ""
    rows: list[dict[str, str]] = []
    state: str = ""
    message: str = ""
    customer_name: str = ""
    customer_email: str = ""
    invoice_identity: str = ""
    notes: str = ""
    issue_date: str = ""
    due_date: str = ""
    line_description: str = ""
    line_quantity: str = "1"
    line_unit_price: str = "0.00"
    tax_label: str = ""
    tax_amount: str = "0.00"
    received_total: str = "0.00"
    issue_open: bool = False
    void_open: bool = False
    is_synthetic_demo: bool = False

    def _id_from_route(self) -> str:
        route_id = self.router_data.get("invoice_id", "")
        return str(route_id) if route_id else self.selected_invoice_id

    def load_invoice(self) -> rx.event.EventSpec | None:
        try:
            owner = self.require_owner()
            self.is_synthetic_demo = is_synthetic_demo_owner(owner)
            record = owner_invoice(owner, self._id_from_route())
        except (AuthenticationError, WorkspaceAccessError):
            return rx.redirect("/sign-in")
        if record is None:
            self.message = "Invoice not found."
            return None
        self.selected_invoice_id, self.state = str(record.id), record.state
        self.customer_name, self.customer_email = record.customer_name, record.customer_email
        self.invoice_identity, self.notes = record.invoice_identity, record.notes
        self.issue_date, self.due_date = (
            record.issue_date.isoformat(),
            record.due_date.isoformat() if record.due_date else "",
        )
        self.received_total = str(record.received_total)
        if record.lines:
            self.line_description, self.line_quantity, self.line_unit_price = (
                record.lines[0]["description"],
                record.lines[0]["quantity"],
                record.lines[0]["unit_price"],
            )
        if record.taxes:
            self.tax_label, self.tax_amount = record.taxes[0]["label"], record.taxes[0]["amount"]
        self.message = ""
        return None

    def load_list(self) -> rx.event.EventSpec | None:
        try:
            owner = self.require_owner()
            self.is_synthetic_demo = is_synthetic_demo_owner(owner)
            records = owner_invoices(owner, self.status_filter)
        except (AuthenticationError, WorkspaceAccessError):
            return rx.redirect("/sign-in")
        self.rows = [
            {
                "id": str(item.id),
                "number": item.invoice_number,
                "customer": item.customer_name,
                "status": item.payment_status.replace("_", " ").title(),
                "total": f"{item.currency} {item.grand_total:.2f}",
            }
            for item in records
        ]
        return None

    def save_draft(self) -> None:
        taxes = (
            []
            if not self.tax_label.strip()
            else [{"label": self.tax_label, "amount": self.tax_amount}]
        )
        result = update_invoice_draft(
            self.require_owner(),
            self.selected_invoice_id,
            {
                "customer_name": self.customer_name,
                "customer_email": self.customer_email,
                "invoice_identity": self.invoice_identity,
                "notes": self.notes,
                "issue_date": self.issue_date,
                "due_date": self.due_date,
                "lines": [
                    {
                        "description": self.line_description,
                        "quantity": self.line_quantity,
                        "unit_price": self.line_unit_price,
                    }
                ],
                "taxes": taxes,
            },
        )
        self.message = result.message
        if result.outcome == "saved":
            self.load_invoice()

    def confirm_issue(self) -> None:
        result = issue_invoice(self.require_owner(), self.selected_invoice_id)
        self.message, self.issue_open = result.message, False
        if result.invoice_id:
            self.load_invoice()

    def save_payment(self) -> None:
        result = set_received_total(
            self.require_owner(), self.selected_invoice_id, self.received_total
        )
        self.message = result.message
        if result.invoice_id:
            self.load_invoice()

    def download_pdf(self) -> rx.event.EventSpec | None:
        self.require_owner()
        return rx.redirect(f"/documents/{self.selected_invoice_id}")

    def email_pdf(self) -> None:
        self.message = queue_invoice_email(
            self.require_owner(), self.selected_invoice_id, "issued_pdf"
        ).message

    def email_payment_update(self) -> None:
        self.message = queue_invoice_email(
            self.require_owner(), self.selected_invoice_id, "payment_update"
        ).message

    def confirm_void(self) -> rx.event.EventSpec | None:
        result = void_and_redraft(self.require_owner(), self.selected_invoice_id)
        self.message, self.void_open = result.message, False
        return rx.redirect(f"/owner/invoices/{result.invoice_id}") if result.invoice_id else None


def owner_invoices_page() -> rx.Component:
    return owner_layout(
        rx.cond(OwnerInvoicesState.is_synthetic_demo, synthetic_demo_banner()),
        rx.vstack(
            rx.heading("Invoices", size="7"),
            rx.text("Create invoices from completed bookings and track payments manually."),
            rx.hstack(
                rx.select(
                    ["All", "Outstanding", "Partially paid", "Paid", "Void"],
                    value=OwnerInvoicesState.status_filter,
                    on_change=OwnerInvoicesState.set_status_filter,
                ),
                rx.button("Apply filter", on_click=OwnerInvoicesState.load_list),
            ),
            rx.foreach(
                OwnerInvoicesState.rows,
                lambda row: rx.card(
                    rx.hstack(
                        rx.vstack(
                            rx.text(row["number"], weight="bold"),
                            rx.text(row["customer"]),
                            align="start",
                        ),
                        rx.text(row["total"]),
                        status_badge(row["status"]),
                        rx.link("View", href="/owner/invoices/" + row["id"]),
                        justify="between",
                        width="100%",
                    )
                ),
            ),
            rx.cond(
                OwnerInvoicesState.rows.length() == 0,
                rx.text("No issued invoices match this filter."),
            ),
            width="100%",
            align="start",
        )
    )


def owner_invoice_detail_page() -> rx.Component:
    def field(label: str, value: rx.Var, change: rx.EventHandler, **kwargs: object) -> rx.Component:
        return rx.vstack(
            rx.el.label(label),
            rx.input(value=value, on_change=change, **kwargs),
            align="start",
            width="100%",
        )

    draft = rx.card(
        rx.vstack(
            rx.heading("Invoice draft", size="5"),
            field(
                "Customer name",
                OwnerInvoicesState.customer_name,
                OwnerInvoicesState.set_customer_name,
            ),
            field(
                "Customer email",
                OwnerInvoicesState.customer_email,
                OwnerInvoicesState.set_customer_email,
                type="email",
            ),
            field(
                "Issue date",
                OwnerInvoicesState.issue_date,
                OwnerInvoicesState.set_issue_date,
                type="date",
            ),
            field(
                "Due date (optional)",
                OwnerInvoicesState.due_date,
                OwnerInvoicesState.set_due_date,
                type="date",
            ),
            field(
                "Line description",
                OwnerInvoicesState.line_description,
                OwnerInvoicesState.set_line_description,
            ),
            field(
                "Quantity",
                OwnerInvoicesState.line_quantity,
                OwnerInvoicesState.set_line_quantity,
                type="number",
            ),
            field(
                "Unit price",
                OwnerInvoicesState.line_unit_price,
                OwnerInvoicesState.set_line_unit_price,
                type="number",
            ),
            field(
                "Tax label (optional)",
                OwnerInvoicesState.tax_label,
                OwnerInvoicesState.set_tax_label,
            ),
            field(
                "Tax amount",
                OwnerInvoicesState.tax_amount,
                OwnerInvoicesState.set_tax_amount,
                type="number",
            ),
            field(
                "Business invoice details",
                OwnerInvoicesState.invoice_identity,
                OwnerInvoicesState.set_invoice_identity,
            ),
            rx.el.label("Notes"),
            rx.text_area(value=OwnerInvoicesState.notes, on_change=OwnerInvoicesState.set_notes),
            rx.text(BIR_BOUNDARY, size="2"),
            rx.hstack(
                rx.button("Save draft", on_click=OwnerInvoicesState.save_draft),
                rx.button(
                    "Review and issue",
                    on_click=OwnerInvoicesState.set_issue_open(True),
                    variant="soft",
                ),
            ),
            width="100%",
            align="start",
        )
    )
    issued = rx.card(
        rx.vstack(
            rx.heading("Issued invoice", size="5"),
            rx.text("This invoice is frozen. Corrections create a new draft."),
            field(
                "Total received",
                OwnerInvoicesState.received_total,
                OwnerInvoicesState.set_received_total,
                type="number",
            ),
            rx.hstack(
                rx.button("Update payment", on_click=OwnerInvoicesState.save_payment),
                rx.button("Download PDF", on_click=OwnerInvoicesState.download_pdf, variant="soft"),
                rx.button("Email PDF", on_click=OwnerInvoicesState.email_pdf, variant="soft"),
                rx.button(
                    "Email payment update",
                    on_click=OwnerInvoicesState.email_payment_update,
                    variant="soft",
                ),
                rx.button(
                    "Void and create new draft",
                    on_click=OwnerInvoicesState.set_void_open(True),
                    color_scheme="red",
                    variant="soft",
                ),
                wrap="wrap",
            ),
            width="100%",
            align="start",
        )
    )
    return owner_layout(
        rx.cond(OwnerInvoicesState.is_synthetic_demo, synthetic_demo_banner()),
        rx.vstack(
            rx.cond(OwnerInvoicesState.state == "draft", draft, issued),
            rx.cond(
                OwnerInvoicesState.message != "",
                feedback(OwnerInvoicesState.message, kind="warning"),
            ),
            rx.dialog.root(
                rx.dialog.content(
                    rx.dialog.title("Issue this invoice?"),
                    rx.dialog.description("This assigns its final number and freezes the PDF."),
                    rx.hstack(
                        rx.dialog.close(rx.button("Keep editing", variant="soft")),
                        rx.dialog.close(
                            rx.button("Issue invoice", on_click=OwnerInvoicesState.confirm_issue)
                        ),
                        justify="end",
                    ),
                ),
                open=OwnerInvoicesState.issue_open,
                on_open_change=OwnerInvoicesState.set_issue_open,
            ),
            rx.dialog.root(
                rx.dialog.content(
                    rx.dialog.title("Void this invoice?"),
                    rx.dialog.description(
                        "The issued PDF and number stay on record. A separate draft will open."
                    ),
                    rx.hstack(
                        rx.dialog.close(rx.button("Keep invoice", variant="soft")),
                        rx.dialog.close(
                            rx.button(
                                "Void and create draft",
                                on_click=OwnerInvoicesState.confirm_void,
                                color_scheme="red",
                            )
                        ),
                        justify="end",
                    ),
                ),
                open=OwnerInvoicesState.void_open,
                on_open_change=OwnerInvoicesState.set_void_open,
            ),
            width="100%",
            align="start",
        )
    )
