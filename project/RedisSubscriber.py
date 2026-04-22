import threading
import time
import queue
from queue import Queue
import redis
import logging

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
            # unlike self.redis_ps_conn.listen(), .get_message() will periodically check _stop_event
            msg = self.redis_ps_conn.get_message()
            # do not include control messages in queue (like subscribe or unsubscribe)
            if msg['type'] == 'message':
                logger.info(f"{self.module_name} received {msg} on {self.registered_sub_channel}")
                self.input_queue.put(msg)
                logger.info(f"{self._thread} added {msg} to {self.input_queue}")
            else:
                time.sleep(0.01)


