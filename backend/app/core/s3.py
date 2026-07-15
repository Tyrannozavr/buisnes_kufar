"""
S3-compatible storage: upload, presigned URL for download, delete.
Works with Cloudflare R2, MinIO, AWS S3.
"""
from __future__ import annotations

import uuid
from typing import Optional

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.core.config import settings


def _client():
    if not settings.S3_ENABLED:
        raise RuntimeError("S3 is not configured. Set S3_BUCKET, S3_ACCESS_KEY, S3_SECRET_KEY.")
    kwargs = {
        "aws_access_key_id": settings.S3_ACCESS_KEY,
        "aws_secret_access_key": settings.S3_SECRET_KEY,
        "region_name": settings.S3_REGION,
        "config": Config(signature_version="s3v4"),
    }
    if settings.S3_ENDPOINT_URL:
        kwargs["endpoint_url"] = settings.S3_ENDPOINT_URL
    return boto3.client("s3", **kwargs)


def _bucket():
    return settings.S3_BUCKET


def ensure_bucket() -> None:
    """Создать бакет, если его ещё нет (свежий MinIO в docker-compose.dev)."""
    if not settings.S3_ENABLED:
        return
    client = _client()
    name = _bucket()
    try:
        client.head_bucket(Bucket=name)
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "")
        status = e.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        if code in ("404", "NoSuchBucket", "NotFound") or status == 404:
            client.create_bucket(Bucket=name)
        else:
            raise


def build_key(prefix: str, *parts: str) -> str:
    parts = [p.strip("/") for p in parts if p]
    return "/".join([prefix.strip("/")] + list(parts))


def upload_document(deal_id: int, filename: str, content: bytes, content_type: Optional[str] = None) -> str:
    """
    Upload document to S3. Returns the S3 key (stored in DB as document_file_path).
    """
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
    key = build_key(
        settings.S3_DOCUMENTS_PREFIX,
        "deals",
        str(deal_id),
        f"{uuid.uuid4().hex}.{ext}",
    )
    client = _client()
    extra = {}
    if content_type:
        extra["ContentType"] = content_type
    try:
        client.put_object(
            Bucket=_bucket(),
            Key=key,
            Body=content,
            **extra,
        )
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "")
        if code == "NoSuchBucket":
            ensure_bucket()
            client.put_object(
                Bucket=_bucket(),
                Key=key,
                Body=content,
                **extra,
            )
        else:
            raise
    return key


def _client_for_presigned():
    """Client для presigned URL: использует S3_PUBLIC_ENDPOINT_URL если задан (доступен из браузера)."""
    base_kwargs = {
        "aws_access_key_id": settings.S3_ACCESS_KEY,
        "aws_secret_access_key": settings.S3_SECRET_KEY,
        "region_name": settings.S3_REGION,
        "config": Config(signature_version="s3v4"),
    }
    endpoint = settings.S3_PUBLIC_ENDPOINT_URL or settings.S3_ENDPOINT_URL
    if endpoint:
        base_kwargs["endpoint_url"] = endpoint
    return boto3.client("s3", **base_kwargs)


def get_presigned_download_url(key: str, expires_in: Optional[int] = None) -> str:
    """Generate presigned URL for GET. Uses S3_PUBLIC_ENDPOINT_URL when set (browser-accessible)."""
    if expires_in is None:
        expires_in = settings.S3_PRESIGNED_EXPIRES
    client = _client_for_presigned()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": _bucket(), "Key": key},
        ExpiresIn=expires_in,
    )


def get_document_content(key: str) -> tuple[bytes, Optional[str]]:
    """Скачать содержимое файла из S3. Возвращает (content, content_type)."""
    client = _client()
    response = client.get_object(Bucket=_bucket(), Key=key)
    body = response["Body"].read()
    content_type = response.get("ContentType")
    return (body, content_type)


def delete_document(key: str) -> bool:
    """Delete object from S3. Returns True if deleted or not found."""
    try:
        _client().delete_object(Bucket=_bucket(), Key=key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return True
        raise
