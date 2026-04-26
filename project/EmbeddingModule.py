import queue
from time import sleep
import redis
import random

from RedisSubscriber import RedisSubscriber
from RedisPublisher import RedisPublisher
from QueueWorker import AnnotationWorker
from message import EmbeddingCreatedMessage
from logger import make_logger

logger = make_logger()

def embedding_generation(msg):
    embedding_dimension = 5
    return [random.random() for _ in range(embedding_dimension)]

# This is the primary function of the Embedding Module and is what the QueueWorker performs when a message arrives
def embedding_process(message_dict, embedding_service_pub):
    # message is a dict NOT type Message! Cannot use Message class methods.
    try:
        # gets message from annotation module "inference_complete" channel
        msg_payload = message_dict['payload']
        image_metadata = msg_payload['image_metadata']

        # performs embedding generation
        embedding_data = embedding_generation(msg_payload)

        # sends a message stating embedding is complete to "embedding_created" channel
        inference_complete_msg = EmbeddingCreatedMessage(image_metadata, embedding_data)
        embedding_service_pub.publish_message("embedding_created", inference_complete_msg)

    except Exception:
        logger.exception("Failed to process message: %r", message_dict)

# Connect to same redis_client as other services
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

# Make a Queue where you want any messages to be stored for worker to work on
embedding_service_sub_queue = queue.Queue(10)
# become a subscriber on redis_client
embedding_service_sub = RedisSubscriber("Annotation Service Subscriber", embedding_service_sub_queue, redis_client)
# subscribe to inference completed channel
embedding_service_sub.register_sub_channel("inference_completed")

# become a publisher on redis_client
embedding_service_pub = RedisPublisher("Embedding Service Publisher", redis_client)
# create a channel called "embedding_created"
embedding_service_pub.register_pub_channel("embedding_created")

# Make a EmbeddingWorker
embedding_service_worker = AnnotationWorker(embedding_service_sub_queue, embedding_process, embedding_service_pub)

# tell the queue worker to begin
embedding_service_worker.start()
sleep(60)
# close the worker
embedding_service_worker.stop()