# https://redis.readthedocs.io/en/stable/advanced_features.html#publish-subscribe

import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

pubsub = r.pubsub()
pubsub.subscribe("sensor_updates", "weather_updates")

print("Waiting for messages...")

# Received: {'type': 'message', 'pattern': None, 'channel': 'sensor_updates', 'data': 'temperature:20'}
for message in pubsub.listen():
    print(f"Received: {message}")
    if message["data"] == "STOP":
        print("Received stop signal") # will break on FIRST stop signal
        break

# for message in pubsub.listen():
    # if message["type"] == "message":
        # print(f"Received: {message['data']}")






