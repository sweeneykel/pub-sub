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
    def __init__(self, input_queue: queue.Queue, process_function):
        self.input_queue = input_queue
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        # here is the function object itself; store it and call it later
        # vs process_function() call it right now
        self._process_function = process_function


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
                logger.info(f"{self._thread} working on a msg")

                self._process(msg)

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
        # TODO: validate this function
        self._process_function(msg)
