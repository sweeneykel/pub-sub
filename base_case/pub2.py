import redis
import time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

channel = "weather_updates"

#Received: {'type': 'message', 'pattern': None, 'channel': 'sensor_updates', 'data': 'temperature:20'}

weather_type_list = ['rain', 'sun', 'snow', 'sleet', 'haze']
for w_type in weather_type_list:
    message = f"weather is:{w_type}"
    r.publish(channel, message)
    print(f"Published: {message}")
    time.sleep(10)

r.publish(channel, "STOP")

