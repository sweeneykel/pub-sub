import redis
from message import Message
import logging

# r = redis.Redis(host='localhost', port=6379, decode_responses=True)

logger = logging.getLogger(__name__)

class Module:
    sys_channels = set()

    @classmethod
    def get_sys_channels(cls):
        return Module.sys_channels

    def __init__(self, module_name: str, redis_pub_conn: redis.Redis):
        self.module_name = module_name
        self.redis_pub_conn = redis_pub_conn
        self.redis_sub_conn = redis_pub_conn.pubsub()
        self.channels_pub = set()
        self.channels_sub = set()
        # TODO: could add message type

    def add_pub_channel(self, channel: str):
        if channel in self.channels_pub:
            raise ValueError(f"Channel '{channel}' already exists")
        self.channels_pub.add(channel)
        Module.sys_channels.add(channel)

    def publish_message(self, channel: str, message: Message):
        if channel not in self.channels_pub:
            raise ValueError(f"Channel '{channel}' not registered to {self.module_name}")

        if not hasattr(message, "to_json"):
            raise TypeError("message must implement to_json()")

        # TODO: could add validation for message type

        payload = message.to_json()
        self.redis_pub_conn.publish(channel, payload)

        logger.info(f"{self.module_name} -> {channel} with {self.redis_pub_conn.pubsub_numsub(channel)} subscribers: {payload}")

    def sub_to_channel(self, channel:str):
        if channel in self.channels_sub:
            raise ValueError(f"Already subscribed to '{channel}'.")

        if channel not in Module.sys_channels:
            raise ValueError(f"{channel} does not exist in system.")

        self.channels_sub.add(channel)
        self.redis_sub_conn.subscribe(channel)
        logger.info(f"{self.module_name} subscribed to {channel}")

    def to_string(self):
        print(f"{self.module_name} can publish on {', '.join(sorted(self.channels_pub))}")



