import queue
import threading
import logging

# move to main to configure for all modules
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)s] %(message)s"
)
# creates a logger named after module
logger = logging.getLogger(__name__)

class QueueWorker:
    def __init__(self, input_queue: queue.Queue):
        self.input_queue = input_queue
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self._thread.start()
        logger.info(f"{self._thread} started")

    def stop(self):
        # stops the worker thread. Does not stop main thread.
        self._stop_event.set() # triggers _run loop to exit
        self._thread.join() # waits for thread in _run to complete
        logger.info(f"{self._thread} stopped")

    def _run(self):
        while not self._stop_event.is_set():
            msg = None
            try:
                msg = self.input_queue.get(timeout=1)
                self._process(msg)
                logger.info("%s processed %r", self._thread, msg)

            except queue.Empty:
                continue

            except Exception:
                logger.exception("Failed to process message: %r", msg)
                # retry/drop/dead-letter policy goes here
                # alternative implementations could be made. issue created.

            finally:
                if msg is not None:
                    self.input_queue.task_done()

    def _process(self, msg):
        # placeholder for doing the action. Black box right now.
        print(f"{self} processing {msg}")