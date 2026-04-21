import mimetypes
import shutil
import uuid
from pathlib import Path

import redis

from RedisPublisher import RedisPublisher
from message_inheritance import ImageSubmittedMessage

class PhotoUploadModule:
    IMAGE_SUBMITTED_CHANNEL = "image_submitted"
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    ALLOWED_MIME_TYPES = {
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
    }

    def __init__(self, redis_client: redis.Redis, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        self.publisher = RedisPublisher("photo_upload_module", redis_client)
        self.publisher.register_pub_channel(self.IMAGE_SUBMITTED_CHANNEL)

    def upload_photo_from_path(self, source_path: str, source: str = "user_upload") -> ImageSubmittedMessage:
        source_file = Path(source_path)

        if not source_file.exists():
            raise FileNotFoundError(f"Photo does not exist: {source_path}")

        if not source_file.is_file():
            raise ValueError(f"Upload path is not a file: {source_path}")

        self._validate_photo(source_file)

        image_id = str(uuid.uuid4())
        saved_path = self._save_photo(source_file, image_id)

        message = ImageSubmittedMessage(
            image_id=image_id,
            path=str(saved_path),
            source=source,
        )

        self.publisher.publish_message(self.IMAGE_SUBMITTED_CHANNEL, message)
        return message

    def _validate_photo(self, source_file: Path):
        extension = source_file.suffix.lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported photo type: {extension}")

        mime_type, _ = mimetypes.guess_type(source_file.name)
        if mime_type not in self.ALLOWED_MIME_TYPES:
            raise ValueError(f"Unsupported MIME type: {mime_type}")

    def _save_photo(self, source_file: Path, image_id: str) -> Path:
        destination = self.upload_dir / f"{image_id}{source_file.suffix.lower()}"
        shutil.copy2(source_file, destination)
        return destination
