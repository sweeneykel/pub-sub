# to do
# labeling feature generate 10 images with boxes OR LLM COCO
# upload completed, analysis with labels

import redis

from PhotoUploadModule import PhotoCliModule

def main():
    redis_client = redis.Redis(
        host="localhost",
        port=6379,
        decode_responses=True,
    )

    # creates an instances of a class from PhotoUploadModule
    cli = PhotoCliModule(redis_client=redis_client)
    cli.run()

if __name__ == "__main__":
    main()