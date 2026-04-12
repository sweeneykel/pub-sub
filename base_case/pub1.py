import redis
import time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

channel = "sensor_updates"

#Received: {'type': 'message', 'pattern': None, 'channel': 'sensor_updates', 'data': 'temperature:20'}

for i in range(5):
    message = f"temperature:{20 + i}"
    r.publish(channel, message)
    print(f"Published: {message}")
    time.sleep(10)

r.publish(channel, "STOP")

