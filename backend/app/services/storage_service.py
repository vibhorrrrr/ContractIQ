"""Storage service — local filesystem or S3 abstraction."""

import os
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings


class StorageService:
    """Handles file storage. Uses local filesystem in dev, S3 in production."""

    def __init__(self) -> None:
        self.mode = settings.STORAGE_MODE
        self.upload_dir = Path(settings.LOCAL_UPLOAD_DIR)

    async def save_file(self, file: UploadFile) -> tuple[str, int]:
        """Save uploaded file and return (file_path, file_size)."""
        if self.mode == "local":
            return await self._save_local(file)
        else:
            raise NotImplementedError("S3 storage not implemented for MVP.")

    async def _save_local(self, file: UploadFile) -> tuple[str, int]:
        """Save file to local uploads directory."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename to avoid collisions
        ext = Path(file.filename or "file").suffix
        unique_name = f"{uuid.uuid4().hex}{ext}"
        file_path = self.upload_dir / unique_name

        content = await file.read()
        file_size = len(content)

        with open(file_path, "wb") as f:
            f.write(content)

        return str(file_path), file_size

    async def get_file_path(self, stored_path: str) -> Path:
        """Resolve a stored path to a local filesystem path."""
        if self.mode == "local":
            return Path(stored_path)
        raise NotImplementedError("S3 storage not implemented for MVP.")

    async def delete_file(self, stored_path: str) -> None:
        """Delete a stored file."""
        if self.mode == "local":
            path = Path(stored_path)
            if path.exists():
                os.remove(path)
