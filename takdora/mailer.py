"""Small, injectable SMTP boundary for transactional owner messages."""

from __future__ import annotations

import smtplib
from dataclasses import dataclass, field
from email.message import EmailMessage

from takdora.config import Settings


class MailDeliveryError(RuntimeError):
    """A bounded message suitable for owner-facing retry feedback."""


@dataclass(frozen=True)
class OutgoingMessage:
    """A concise transactional message with no credential material."""

    recipient: str
    subject: str
    body: str
    attachment: bytes | None = None
    attachment_filename: str | None = None


class Mailer:
    """SMTP-backed mail sender; provider configuration never reaches browser state."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def _send(self, message: OutgoingMessage) -> None:
        if not self._settings.smtp_host or not self._settings.mail_from:
            raise MailDeliveryError("We could not send that email yet. Please try again shortly.")
        email = EmailMessage()
        email["From"] = self._settings.mail_from
        email["To"] = message.recipient
        email["Subject"] = message.subject
        email.set_content(message.body)
        if message.attachment is not None and message.attachment_filename:
            email.add_attachment(
                message.attachment,
                maintype="application",
                subtype="pdf",
                filename=message.attachment_filename,
            )
        try:
            with smtplib.SMTP(
                self._settings.smtp_host, self._settings.smtp_port, timeout=10
            ) as client:
                client.starttls()
                if self._settings.smtp_username and self._settings.smtp_password:
                    client.login(self._settings.smtp_username, self._settings.smtp_password)
                client.send_message(email)
        except (OSError, smtplib.SMTPException) as error:
            raise MailDeliveryError(
                "We could not send that email yet. Please try again shortly."
            ) from error

    def send_verification(self, recipient: str, verification_url: str) -> None:
        self._send(
            OutgoingMessage(
                recipient=recipient,
                subject="Verify your Takdora email",
                body=(
                    "Verify your email to publish your Takdora business.\n\n"
                    f"Open this link within 30 minutes: {verification_url}"
                ),
            )
        )

    def send_password_reset(self, recipient: str, reset_url: str) -> None:
        self._send(
            OutgoingMessage(
                recipient=recipient,
                subject="Reset your Takdora password",
                body=(
                    "Use this one-time link within 30 minutes to reset your Takdora sign-in.\n\n"
                    f"{reset_url}"
                ),
            )
        )

    def send_booking_confirmation(self, recipient: str, subject: str, body: str) -> None:
        self._send(OutgoingMessage(recipient, subject, body))

    def send_invoice_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        *,
        pdf: bytes | None = None,
        filename: str = "",
    ) -> None:
        self._send(OutgoingMessage(recipient, subject, body, pdf, filename or None))


@dataclass
class InMemoryMailer:
    """A test double that records safe mail content without a network call."""

    fail_delivery: bool = False
    sent_messages: list[OutgoingMessage] = field(default_factory=list)

    def _send(self, message: OutgoingMessage) -> None:
        if self.fail_delivery:
            raise MailDeliveryError("We could not send that email yet. Please try again shortly.")
        self.sent_messages.append(message)

    def send_verification(self, recipient: str, verification_url: str) -> None:
        self._send(
            OutgoingMessage(
                recipient, "Verify your Takdora email", f"Verify your email: {verification_url}"
            )
        )

    def send_password_reset(self, recipient: str, reset_url: str) -> None:
        self._send(
            OutgoingMessage(
                recipient, "Reset your Takdora password", f"Reset password: {reset_url}"
            )
        )

    def send_booking_confirmation(self, recipient: str, subject: str, body: str) -> None:
        self._send(OutgoingMessage(recipient, subject, body))

    def send_invoice_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        *,
        pdf: bytes | None = None,
        filename: str = "",
    ) -> None:
        self._send(OutgoingMessage(recipient, subject, body, pdf, filename or None))
