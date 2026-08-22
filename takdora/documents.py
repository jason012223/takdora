"""Private, server-owned object storage for durable business assets."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from uuid import uuid4

from botocore.client import BaseClient

from takdora.config import Settings

MAX_LOGO_BYTES = 2 * 1024 * 1024
ALLOWED_LOGO_TYPES = {"image/png", "image/jpeg", "image/webp"}
PDF_CONTENT_TYPE = "application/pdf"


class DocumentStorageError(ValueError):
    """Return a bounded storage failure without provider details."""


@dataclass(frozen=True)
class StoredDocument:
    key: str
    byte_size: int
    checksum_sha256: str
    content_type: str


def _client(settings: Settings) -> BaseClient:
    if not all(
        (
            settings.object_storage_endpoint_url,
            settings.object_storage_bucket,
            settings.object_storage_access_key_id,
            settings.object_storage_secret_access_key,
            settings.object_storage_region,
        )
    ):
        raise DocumentStorageError("Private storage is not configured.")
    import boto3

    return boto3.client(
        "s3",
        endpoint_url=settings.object_storage_endpoint_url,
        aws_access_key_id=settings.object_storage_access_key_id,
        aws_secret_access_key=settings.object_storage_secret_access_key,
        region_name=settings.object_storage_region,
    )


def invoice_storage_key(business_id: int) -> str:
    return f"businesses/{business_id}/invoices/{uuid4().hex}.pdf"


def logo_storage_key(business_id: int, content_type: str) -> str:
    extension = {"image/png": "png", "image/jpeg": "jpg", "image/webp": "webp"}.get(content_type)
    if extension is None:
        raise DocumentStorageError("Use a PNG, JPEG, or WebP logo.")
    return f"businesses/{business_id}/logos/{uuid4().hex}.{extension}"


def store_private_bytes(
    settings: Settings,
    business_id: int,
    content: bytes,
    content_type: str,
    *,
    key: str,
    client: BaseClient | None = None,
) -> StoredDocument:
    """Write only server-generated private keys; browser keys are never accepted."""
    if (
        business_id <= 0
        or not content
        or (content_type == PDF_CONTENT_TYPE and not content.startswith(b"%PDF"))
    ):
        raise DocumentStorageError("The document could not be stored.")
    if content_type in ALLOWED_LOGO_TYPES and len(content) > MAX_LOGO_BYTES:
        raise DocumentStorageError("Logo files must be 2 MB or smaller.")
    if content_type not in ALLOWED_LOGO_TYPES | {PDF_CONTENT_TYPE}:
        raise DocumentStorageError("Unsupported document type.")
    if not key.startswith(f"businesses/{business_id}/"):
        raise DocumentStorageError("The document could not be stored.")
    digest = hashlib.sha256(content).hexdigest()
    try:
        (_client(settings) if client is None else client).put_object(
            Bucket=settings.object_storage_bucket,
            Key=key,
            Body=content,
            ContentType=content_type,
            ACL="private",
        )
    except Exception as error:
        raise DocumentStorageError("The document could not be stored.") from error
    return StoredDocument(key, len(content), digest, content_type)


def presigned_download(
    settings: Settings,
    *,
    key: str,
    filename: str,
    client: BaseClient | None = None,
) -> str:
    """Generate a five-minute attachment URL only after caller authorizes its record."""
    if not key.startswith("businesses/") or not filename.endswith(".pdf"):
        raise DocumentStorageError("Document not found.")
    try:
        return (_client(settings) if client is None else client).generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.object_storage_bucket,
                "Key": key,
                "ResponseContentDisposition": f'attachment; filename="{filename}"',
                "ResponseContentType": PDF_CONTENT_TYPE,
            },
            ExpiresIn=300,
        )
    except Exception as error:
        raise DocumentStorageError("Document not found.") from error


def read_private_bytes(settings: Settings, *, key: str, client: BaseClient | None = None) -> bytes:
    """Read a private object only from a server-side delivery path."""
    if not key.startswith("businesses/"):
        raise DocumentStorageError("Document not found.")
    try:
        response = (_client(settings) if client is None else client).get_object(
            Bucket=settings.object_storage_bucket, Key=key
        )
        return response["Body"].read()
    except Exception as error:
        raise DocumentStorageError("Document not found.") from error
