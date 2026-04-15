import redis
from src.project.message_inheritance import InferenceCompletedMessage
import json

r = redis.Redis(host="localhost", port=6379, decode_responses=True)
channel = "ImageService"

pubsub = r.pubsub()
pubsub.subscribe("ImageSubmitted")

print("Waiting for messages...")


# create module (redis.Redis, channel = r.pubsub())
# subscribe to x channel
# publish x message

for incoming_message in pubsub.listen():  #incoming_message is type dict
    # Received: {'type': 'message', 'pattern': None, 'channel': 'sensor_updates', 'data': 'temperature:20'}
    if incoming_message['type'] == 'message':
        if incoming_message["data"] == "STOP":
            print("Received stop signal") # will break on FIRST stop signal since pubsub.listen() is blocking
            break

        print(f"{channel} received an incoming message: {incoming_message['data']}") #incoming_message['data'] is type str

        # TODO: wondering what type of structure the annotation_metadata will be
        with open('annotation_metadata.json', 'r') as file:
            annotation_metadata = json.load(file)
        image_metadata = json.loads(incoming_message['data'])  # image_metadata is of type dict

        outgoing_message = InferenceCompletedMessage(image_metadata['payload'], annotation_metadata)
        print(f"{channel} is sending an outgoing message: {outgoing_message.to_json()}")
        #r.publish(channel, msg1.to_json())
        #print(f"{channel} published: {msg1.to_json()}")