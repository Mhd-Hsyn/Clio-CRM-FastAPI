import uuid
from pathlib import Path
from fastapi import UploadFile
from typing import Optional
from app.config.storage.factory import storage
from app.core.exceptions.base import AppException
from app.config.logger import get_logger

logger = get_logger("file_utils")

# Configure allowed types and max size (bytes)
ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_FILE_EXTS = ALLOWED_IMAGE_EXTS.union({".pdf", ".docx", ".txt"})
MAX_UPLOAD_SIZE = 25 * 1024 * 1024  # 25 MB


async def _validate_file(file: UploadFile, allowed_exts: set, max_size: int):
    """Validate file extension and size."""
    if not file or not file.filename:
        raise AppException("No file provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in allowed_exts:
        raise AppException(f"Unsupported file type: {ext}")

    total = 0
    while chunk := await file.read(64 * 1024):
        total += len(chunk)
        if total > max_size:
            await file.seek(0)
            raise AppException("File too large")
    await file.seek(0)


def _resolve_upload_path(upload_to: str, instance, original_filename: str) -> str:
    """
    Generate final file path using `upload_to` metadata.
    Supports placeholders like `{id}` or `{uuid}`.
    """
    ext = Path(original_filename).suffix.lower()
    file_uuid = uuid.uuid4().hex

    # Replace placeholders if any
    upload_to = upload_to.format(
        id=getattr(instance, "id", None) or file_uuid,
        uuid=file_uuid
    ).rstrip("/")

    return f"{upload_to}/{file_uuid}{ext}"


async def save_file_for_field(
    instance,
    field_name: str,
    file: UploadFile | None,
    *,
    allowed_exts: Optional[set] = None,
    max_size: Optional[int] = None,
) -> Optional[str]:
    if not file:
        return None

    # SQLAlchemy: get upload_to from Column.info or fallback mapping
    upload_to = getattr(instance.__class__, "__file_fields__", {}).get(field_name)
    if not upload_to and hasattr(instance.__class__, "__table__"):
        col = instance.__class__.__table__.columns.get(field_name)
        if col is not None:
            upload_to = col.info.get("upload_to")

    if not upload_to:
        raise AppException(
            f"Missing `upload_to` metadata for field '{field_name}' in model '{instance.__class__.__name__}'."
        )

    allowed_exts = allowed_exts or ALLOWED_FILE_EXTS
    max_size = max_size or MAX_UPLOAD_SIZE
    await _validate_file(file, allowed_exts, max_size)

    path = _resolve_upload_path(upload_to, instance, file.filename)
    await storage.save(path, file)
    return path


