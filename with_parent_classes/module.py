import redis
from message import Message
import logging

# r = redis.Redis(host='localhost', port=6379, decode_responses=True)

logger = logging.getLogger(__name__)

class Module:

    def __init__(self, module_name: str, redis_connection: redis.Redis):
        self.module_name = module_name
        self.redis_connection = redis_connection
        self.channels = set()
        # TODO: could add message type?

    def add_channel(self, channel: str):
        if channel in self.channels:
            raise ValueError(f"Channel '{channel}' already exists")
        self.channels.add(channel)

    def publish_message(self, channel: str, message: Message):
        if channel not in self.channels:
            raise ValueError(f"Channel '{channel}' not registered")

        if not hasattr(message, "to_json"):
            raise TypeError("message must implement to_json()")

        payload = message.to_json()
        self.redis_connection.publish(channel, payload)

        logger.info(f"{self.module_name} -> {channel}: {payload}")


    #def to_string(self):



