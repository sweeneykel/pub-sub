import queue
from time import sleep
from QueueWorker import QueueWorker
from RedisSubscriber import RedisSubscriber
import redis
from AnnotationGUI import annotate_image

from message_inheritance import ImageSubmittedMessage
from message_inheritance import AnnotationCompletedMessage

# This is the primary function of the Annotation Module and is what the QueueWorker performs when a message arrives
def annotation_process(message_dict):
    # message is a dict NOT type Message! Cannot use Message class methods.
    # {'type': 'publish',
    # 'topic': 'image_submitted',
    # 'event_id': 'IS_1',
    #  'payload': {'image_id': 'some_id',
    #              'path': 'photos\\some_id',
    #              'source': 'user_upload'}}
    annotation_metadata = annotate_image(message_dict['payload']['path'])
    return True

# Make a Queue where you want any messages to be stored for worker to work on
annotation_service_queue = queue.Queue(10)
# Connect to same redis_client as other services
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
# become a subscriber on redis_client
annotation_service = RedisSubscriber("Annotation Service", annotation_service_queue, redis_client)
# subscribe to image_submitted channel
annotation_service.register_sub_channel("image_submitted")
# Make a queueworker that gets any messages in the annotation_service_queue and performs the annotation_process on
annotation_service_worker = QueueWorker(annotation_service_queue, annotation_process)
# tell the queue worker to begin
annotation_service_worker.start()
sleep(200)
# close the worker
annotation_service_worker.stop()
