from src.project.message_inheritance import ImageSubmittedMessage
import redis
import time

# create a channel and name it
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
channel = "ImageSubmitted"

# when an image is submitted, publish event (message)
outgoing_message = ImageSubmittedMessage("test_image_id", "test_path_passed", "test_source_passed")

# publish the message
r.publish(channel, outgoing_message.to_json())

# for decoding
print(f"{channel} is sending an outgoing message: {outgoing_message.to_json()}")

# some sort of STOP feature because subscribe is blocking
time.sleep(15)
r.publish(channel, "STOP")

