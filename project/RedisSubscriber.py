import threading
import queue
import redis
import logging
import json

# move to main to configure for all modules
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)s] %(message)s"
)
# creates a logger named after module
logger = logging.getLogger(__name__)

class RedisSubscriber:
    def __init__(self, module_name: str, input_queue: queue.Queue, redis_client: redis.Redis):
        self.module_name = module_name
        self.redis_ps_conn = redis_client.pubsub()
        self.input_queue = input_queue
        self.registered_sub_channel = None
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._stop_event = threading.Event()

    def register_sub_channel(self, channel_name: str):
        # Module registers interest to listen to channel messages
        if self.registered_sub_channel is None:
            self.redis_ps_conn.subscribe(channel_name)
            self.registered_sub_channel = channel_name
            logger.info(f"{self.module_name} subscribed to {channel_name}")
            self._start()
        else:
            raise AttributeError(f"Already subscribed to {self.registered_sub_channel}.")

    def _start(self):
        self._thread.start()

    def stop(self):
        # stops the worker thread. Does not stop main thread.
        self._stop_event.set() # triggers _run loop to exit
        self._thread.join() # waits for thread in _run to complete

    def _run(self):
        while not self._stop_event.is_set():

            # self.redis_ps_conn.get_message() checks VERY FREQUENTLY!!!
            # msg returns None if no message. unlike self.redis_ps_conn.listen(), .get_message() will periodically check _stop_event
            msg = self.redis_ps_conn.get_message()

            if msg is None:
                # check if self._stop_event.is_set()
                continue

            if msg["type"] != "message":
                # check if self._stop_event.is_set()
                continue

            # Only when actionable message arrives
            # msg in RedisSubscriber is dict
            logger.info(f"{self.module_name} received a message from {self.registered_sub_channel}")
            payload = json.loads(msg["data"])
            # payload in RedisSubscriber is dict
            self.input_queue.put(payload)