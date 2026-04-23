import mimetypes
import shutil
import uuid
from pathlib import Path

import redis

from RedisPublisher import RedisPublisher
from message_inheritance import (
    ImageSubmittedMessage,
    QueryImagesSubmitted,
    QueryTopicsSubmitted,
)

class PhotoCliModule:
    IMAGE_SUBMITTED_CHANNEL = "image_submitted"
    QUERY_IMAGES_CHANNEL = "query_images_submitted"
    QUERY_TOPICS_CHANNEL = "query_topics_submitted"

    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    ALLOWED_MIME_TYPES = {
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
    }

    def __init__(self, redis_client: redis.Redis, upload_dir: str = "project/photos"):
        # "project/photos" always
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        self.publisher = RedisPublisher("photo_cli_module", redis_client)
        self.publisher.register_pub_channel(self.IMAGE_SUBMITTED_CHANNEL)
        self.publisher.register_pub_channel(self.QUERY_IMAGES_CHANNEL)
        self.publisher.register_pub_channel(self.QUERY_TOPICS_CHANNEL)

    def run(self):
        while True:
            self._print_menu()
            choice = input("Select an option: ").strip()

            if choice == "1":
                self._handle_upload_file()
            elif choice == "2":
                self._handle_query_by_topic()
            elif choice == "3":
                self._handle_query_by_image()
            elif choice == "4":
                print("Exiting.")
                break
            else:
                print("Invalid option. Please select 1, 2, 3, or 4.")

    def upload_photo_from_path(self, photo_path: str, source: str = "user_upload") -> ImageSubmittedMessage:
        # creates a Path object from photo_path
        filesystem_photo_path = Path(photo_path)

        if not filesystem_photo_path.exists():
            raise FileNotFoundError(f"Photo does not exist: {photo_path}")

        if not filesystem_photo_path.is_file():
            raise ValueError(f"Upload path is not a file: {photo_path}")

        self._validate_photo(filesystem_photo_path)

        image_id = str(uuid.uuid4())
        saved_path = self._save_photo(filesystem_photo_path, image_id)

        message = ImageSubmittedMessage(
            image_id=image_id,
            path=str(saved_path),
            source=source,
        )

        self.publisher.publish_message(self.IMAGE_SUBMITTED_CHANNEL, message)
        return message

    def query_by_topic(self, topic: str, k: int) -> QueryTopicsSubmitted:
        if not topic:
            raise ValueError("Topic cannot be empty")

        self._validate_k(k)

        message = QueryTopicsSubmitted(
            query_topics_submitted=topic,
            k=k,
        )

        self.publisher.publish_message(self.QUERY_TOPICS_CHANNEL, message)
        return message

    def query_by_image(self, image_path: str, k: int) -> QueryImagesSubmitted:
        source_file = Path(image_path)

        if not source_file.exists():
            raise FileNotFoundError(f"Image does not exist: {image_path}")

        if not source_file.is_file():
            raise ValueError(f"Image path is not a file: {image_path}")

        self._validate_photo(source_file)
        self._validate_k(k)

        message = QueryImagesSubmitted(
            query_images_submitted=str(source_file),
            k=k,
        )

        self.publisher.publish_message(self.QUERY_IMAGES_CHANNEL, message)
        return message

    def _handle_upload_file(self):
        photo_path = input("Enter photo path: ").strip() # strip just removes whitespace

        try:
            message = self.upload_photo_from_path(photo_path)
        except Exception as exc:
            print(f"Upload failed: {exc}")

    def _handle_query_by_topic(self):
        topic = input("Enter topic: ").strip()
        k = self._read_k()

        try:
            message = self.query_by_topic(topic, k)
            print("Published topic query:")
            print(message.to_json())
        except Exception as exc:
            print(f"Topic query failed: {exc}")

    def _handle_query_by_image(self):
        image_path = input("Enter image path: ").strip()
        k = self._read_k()

        try:
            message = self.query_by_image(image_path, k)
            print("Published image query:")
            print(message.to_json())
        except Exception as exc:
            print(f"Image query failed: {exc}")

    def _read_k(self) -> int:
        while True:
            raw_value = input("Enter k: ").strip()

            try:
                k = int(raw_value)
                self._validate_k(k)
                return k
            except ValueError as exc:
                print(f"Invalid k: {exc}")

    def _validate_k(self, k: int):
        if k <= 0:
            raise ValueError("k must be greater than 0")

    def _validate_photo(self, source_file: Path):
        extension = source_file.suffix.lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported photo type: {extension}")

        mime_type, _ = mimetypes.guess_type(source_file.name)
        if mime_type not in self.ALLOWED_MIME_TYPES:
            raise ValueError(f"Unsupported MIME type: {mime_type}")

#    saved_path = self._save_photo(filesystem_photo_path, image_id)
    def _save_photo(self, filesystem_photo_path: Path, image_id: str) -> Path:
        # self.upload_dir = project/photos
        # filesystem_photo_path = project/photos/NAMEOFPHOTO.jpg <- user typed
        # filesystem_photo_path.stem = NAMEOFPHOTO
        # filesystem_photo_path.suffix.lower() = .jpg
        destination = self.upload_dir / "photo_uploads" / f"{filesystem_photo_path.stem}{filesystem_photo_path.suffix.lower()}"
        shutil.copy2(filesystem_photo_path, destination)
        return destination

    def _print_menu(self):
        print()
        print("Photo Search CLI")
        print("1) Upload file")
        print("2) Find k similar items by topic")
        print("3) Find k similar items by image")
        print("4) Exit")