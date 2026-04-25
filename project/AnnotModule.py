import queue
from time import sleep
from QueueWorker import AnnotationWorker
from RedisSubscriber import RedisSubscriber
import redis
from AnnotGUI import user_annotates_image
from logger import make_logger
from RedisPublisher import RedisPublisher
from message import AnnotationCompletedMessage

logger = make_logger()

# This is the primary function of the Annotation Module and is what the QueueWorker performs when a message arrives
def annotation_process(message_dict, annot_service_pub):
    # message is a dict NOT type Message! Cannot use Message class methods.
    try:
        annotation_metadata = user_annotates_image(message_dict['payload']['path'])
        print("This is the annotation_metadata: ", annotation_metadata)
        image_metadata = message_dict['payload']
        inference_complete_msg = AnnotationCompletedMessage(image_metadata, annotation_metadata)
        annot_service_pub.publish_message("inference_completed", inference_complete_msg)

    except Exception:
        logger.exception("Failed to process message: %r", message_dict)

# Connect to same redis_client as other services
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

# Make a Queue where you want any messages to be stored for worker to work on
annotation_service_sub_queue = queue.Queue(10)
# become a subscriber on redis_client
annotation_service_sub = RedisSubscriber("Annotation Service Subscriber", annotation_service_sub_queue, redis_client)
# subscribe to image_submitted channel
annotation_service_sub.register_sub_channel("image_submitted")

# become a publisher on redis_client
annotation_service_pub = RedisPublisher("Annotation Service Publisher", redis_client)
# create a channel called "inference_completed"
annotation_service_pub.register_pub_channel("inference_completed")

# Make a AnnotationWorker
annotation_service_worker = AnnotationWorker(annotation_service_sub_queue, annotation_process, annotation_service_pub)

# tell the queue worker to begin
annotation_service_worker.start()
sleep(60)
# close the worker
annotation_service_worker.stop()