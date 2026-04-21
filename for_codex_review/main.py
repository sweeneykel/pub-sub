import redis

from PhotoUploadModule import PhotoUploadModule


redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
)

uploader = PhotoUploadModule(redis_client)

uploader.upload_photo_from_path("photos/cat.jpg")
uploader.upload_photo_from_path("photos/dog.png")
