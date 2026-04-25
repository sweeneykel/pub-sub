import queue
from pymongo import MongoClient
from RedisSubscriber import RedisSubscriber
import redis
from QueueWorker import QueueWorker
from time import sleep
from RedisPublisher import RedisPublisher
from message_inheritance import AnnotationStoredMessage

from logger import make_logger

logger = make_logger()


# This is the primary function of the Annotation DB Module and is what the QueueWorker performs when a message arrives
def mongo_db_process(message_dict, mong_db_service_pub):
    # message is a dict NOT type Message! Cannot use Message class methods.
    try:

        collection.insert_one(message_dict['payload'])
        #annotation_stored_msg = AnnotationStoredMessage(message_dict['payload'])
        #mong_db_service_pub.publish_message("annotation_stored", annotation_stored_msg)
    except Exception:
        logger.exception("Failed to process message: %r", message_dict)

# Connect to same redis_client as other services
redis_client = redis.Redis(host="localhost",port=6379,decode_responses=True)

# Make a Queue where you want any messages to be stored for worker to work on
mongo_db_queue = queue.Queue(10)
# become a subscriber on redis_client
mongo_db_service_sub = RedisSubscriber("Mongo Database", mongo_db_queue, redis_client)
# subscribe to inference_completed channel
mongo_db_service_sub.register_sub_channel("inference_completed")

# become a publisher on redis_client
mongo_db_service_pub = RedisPublisher("Annotation DB Publisher", redis_client)
# create a channel called "inference_completed"
mongo_db_service_pub.register_pub_channel("annotation_stored")

# Set up Document DB (Mongo)
client = MongoClient("mongodb://localhost:27017/")
db = client["annotation_db_01"]
collection = db["table_01"]

# Make a queueworker
# queueworkers always get a queue to work out of
# a function/task specific to the module to complete
# a channel to publish when function/task is complete
annotation_service_worker = QueueWorker(mongo_db_queue, mongo_db_process, mongo_db_service_pub)

# tell the queue worker to begin
annotation_service_worker.start()
sleep(30)
# close the worker
annotation_service_worker.stop()