import json
from pathlib import Path

import pytest

from project.PhotoUploadModule import PhotoCliModule
from project.message import ImageSubmittedMessage


class FakeRedis:
    def __init__(self):
        self.published_messages = []

    def publish(self, channel, payload):
        self.published_messages.append((channel, payload))
        return 1


def test_upload_photo_from_path_copies_file_returns_message_and_publishes(tmp_path):
    # Arrange
    source_photo = tmp_path / "cell.jpg"
    source_photo.write_bytes(b"fake image data")

    upload_dir = tmp_path / "photos"
    (upload_dir / "photo_uploads").mkdir(parents=True)

    fake_redis = FakeRedis()
    module = PhotoCliModule(redis_client=fake_redis, upload_dir=str(upload_dir))

    # Act
    message = module.upload_photo_from_path(str(source_photo))

    # Assert
    assert isinstance(message, ImageSubmittedMessage)
    assert message.topic == "image_submitted"
    assert message.payload["source"] == "user_upload"
    assert message.payload["path"] == str(upload_dir / "photo_uploads" / "cell.jpg")

    copied_photo = upload_dir / "photo_uploads" / "cell.jpg"
    assert copied_photo.exists()
    assert copied_photo.read_bytes() == b"fake image data"

    assert len(fake_redis.published_messages) == 1

    published_channel, published_payload = fake_redis.published_messages[0]
    assert published_channel == "image_submitted"

    published_json = json.loads(published_payload)
    assert published_json["topic"] == "image_submitted"
    assert published_json["payload"] == message.payload


def test_upload_photo_from_path_raises_when_file_does_not_exist(tmp_path):
    fake_redis = FakeRedis()
    module = PhotoCliModule(redis_client=fake_redis, upload_dir=str(tmp_path))

    missing_photo = tmp_path / "missing.jpg"

    with pytest.raises(FileNotFoundError, match="Photo does not exist"):
        module.upload_photo_from_path(str(missing_photo))

    assert fake_redis.published_messages == []

def test_upload_photo_from_path_raises_when_path_is_directory(tmp_path):
    fake_redis = FakeRedis()
    module = PhotoCliModule(redis_client=fake_redis, upload_dir=str(tmp_path))

    directory_path = tmp_path / "not_a_file"
    directory_path.mkdir()

    with pytest.raises(ValueError, match="Upload path is not a file"):
        module.upload_photo_from_path(str(directory_path))

    assert fake_redis.published_messages == []

def test_upload_photo_from_path_raises_for_unsupported_extension(tmp_path):
    fake_redis = FakeRedis()
    module = PhotoCliModule(redis_client=fake_redis, upload_dir=str(tmp_path))

    source_file = tmp_path / "notes.txt"
    source_file.write_text("not an image")

    with pytest.raises(ValueError, match="Unsupported photo type"):
        module.upload_photo_from_path(str(source_file))

    assert fake_redis.published_messages == []

