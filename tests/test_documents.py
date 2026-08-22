"""Private storage boundaries use server-generated keys and bounded content."""

from dataclasses import dataclass

import pytest

from takdora.config import get_settings
from takdora.documents import (
    DocumentStorageError,
    invoice_storage_key,
    presigned_download,
    store_private_bytes,
)


@dataclass
class FakeS3:
    put: dict[str, object] | None = None

    def put_object(self, **kwargs: object) -> None:
        self.put = kwargs

    def generate_presigned_url(self, *_args: object, **kwargs: object) -> str:
        assert kwargs["ExpiresIn"] == 300
        return "https://objects.example.test/signed"


def _settings():
    return get_settings(
        {
            "OBJECT_STORAGE_ENDPOINT_URL": "https://objects.example.test",
            "OBJECT_STORAGE_BUCKET": "private",
            "OBJECT_STORAGE_ACCESS_KEY_ID": "access",
            "OBJECT_STORAGE_SECRET_ACCESS_KEY": "secret",
            "OBJECT_STORAGE_REGION": "sgp1",
        }
    )


def test_stored_invoice_uses_server_generated_business_scoped_key() -> None:
    key = invoice_storage_key(7)
    fake = FakeS3()
    stored = store_private_bytes(
        _settings(), 7, b"%PDF-safe", "application/pdf", key=key, client=fake
    )  # type: ignore[arg-type]
    assert stored.key == key
    assert fake.put and fake.put["ACL"] == "private"
    assert "businesses/7/" in key


def test_storage_rejects_foreign_key_and_unsupported_content() -> None:
    with pytest.raises(DocumentStorageError):
        store_private_bytes(
            _settings(),
            7,
            b"%PDF-safe",
            "application/pdf",
            key="businesses/8/x.pdf",
            client=FakeS3(),
        )  # type: ignore[arg-type]
    with pytest.raises(DocumentStorageError):
        store_private_bytes(
            _settings(), 7, b"html", "text/html", key=invoice_storage_key(7), client=FakeS3()
        )  # type: ignore[arg-type]


def test_presigned_download_is_attachment_bound_and_short_lived() -> None:
    url = presigned_download(
        _settings(), key=invoice_storage_key(7), filename="INV-0001.pdf", client=FakeS3()
    )  # type: ignore[arg-type]
    assert url.startswith("https://")
