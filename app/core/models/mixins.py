# app/core/mixins/file_handler.py
from sqlalchemy.orm import Session
from app.core.exceptions.base import AppException
from app.core.utils.save_images import save_file_for_field
from app.config.storage.factory import storage
from app.config.logger import get_logger
from app.config.database import save_instance


logger = get_logger("file_handler")

class FileHandlerMixin:
    async def save_file(
        self,
        field_name: str,
        upload_file,
        *,
        delete_old: bool = True,
        background_delete: bool = True,
        db: Session
    ) -> str:
        if not upload_file:
            raise AppException(f"No file provided for '{field_name}'")

        old_path = getattr(self, field_name, None)
        new_path = await save_file_for_field(self, field_name, upload_file)

        # assign + persist model
        setattr(self, field_name, new_path)
        await save_instance(self, db)
        if delete_old and old_path and old_path != new_path:
            await self._delete_file_safe(old_path, background=background_delete)

        return new_path

    async def delete_file_field(self, field_name: str, db: Session):
        path = getattr(self, field_name, None)
        if path:
            await self._delete_file_safe(path)
            setattr(self, field_name, None)
            await save_instance(self, db)

    async def _delete_file_safe(self, path: str, background: bool = True):
        try:
            if background:
                # You can integrate Celery or asyncio.create_task here for async background deletion
                await storage.delete(path)
            else:
                await storage.delete(path)
        except Exception as e:
            logger.warning(f"Failed to delete file {path}: {e}")
