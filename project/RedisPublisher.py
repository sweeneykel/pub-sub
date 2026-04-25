import redis
from message import Message

# r is Redis Client. Thread safe and okay to share across modules.
# r = redis.Redis(host='localhost', port=6379, decode_responses=True)

from logger import make_logger

logger = make_logger()

class RedisPublisher:
    def __init__(self, module_name: str, redis_client: redis.Redis):
        self.module_name = module_name
        self.redis = redis_client
        self.registered_pub_channels = set()

    def register_pub_channel(self, channel: str):
        if channel in self.registered_pub_channels:
            raise ValueError(f"Channel '{channel}' already exists")
        self.registered_pub_channels.add(channel)

    def publish_message(self, channel: str, message: Message):
        if channel not in self.registered_pub_channels:
            raise ValueError(f"Channel '{channel}' not registered to {self.module_name}")

        if not isinstance(message, Message):
            raise TypeError("Message must be of type message.")

        payload = message.to_json()
        num_subscribers = self.redis.publish(channel, payload)

        logger.info(f"{self.module_name} published to -> channel {channel} with {num_subscribers} subscribers")

    def to_string(self):
        return f"{self.module_name} can publish on {', '.join(sorted(self.registered_pub_channels))}"
