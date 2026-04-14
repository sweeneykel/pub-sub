import redis
from message_inheritance import InferenceCompletedMessage
import json

r = redis.Redis(host="localhost", port=6379, decode_responses=True)
channel = "DocumentDB"

pubsub = r.pubsub()
pubsub.subscribe("ImageService")

print("Waiting for messages...")

# Received: {'type': 'message', 'pattern': None, 'channel': 'sensor_updates', 'data': 'temperature:20'}
for message in pubsub.listen():
    print(f"{channel} received: {message['data']}")
    if message["data"] == "STOP":
        print("Received stop signal") # will break on FIRST stop signal since pubsub.listen() is blocking
        break