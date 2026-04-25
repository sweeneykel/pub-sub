import queue

from pymongo import MongoClient
from RedisSubscriber import RedisSubscriber
import redis
from QueueWorker import QueueWorker
from time import sleep

client = MongoClient("mongodb://localhost:27017/")
db = client["my_database"]
collection = db["my_collection"]

# This is the primary function of the Annotation Module and is what the QueueWorker performs when a message arrives
def mongo_db_process(message_dict):
    collection.insert_one(message_dict['payload'])

# Make a Queue where you want any messages to be stored for worker to work on
mongo_db_queue = queue.Queue(10)
# Connect to same redis_client as other services
redis_client = redis.Redis(host="localhost",port=6379,decode_responses=True)
# become a subscriber on redis_client
mongo_db_service = RedisSubscriber("Mongo Database", mongo_db_queue, redis_client)
# subscribe to inference_completed channel
mongo_db_service.registered_sub_channel("inference_completed")
# Make a queueworker that gets any messages in the annotation_service_queue and performs the annotation_process on
annotation_service_worker = QueueWorker(mongo_db_queue, mongo_db_process)
# tell the queue worker to begin
annotation_service_worker.start()
sleep(30)
# close the worker
annotation_service_worker.stop()