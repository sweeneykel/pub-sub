import queue
import threading

from logger import make_logger

logger = make_logger()

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
        # self._process_function(msg, self._service_pub_channel)
        raise NotImplementedError


class AnnotationWorker(QueueWorker):
    def __init__(self, input_queue, process_function, publisher):
        super().__init__(input_queue)
        self._process_function = process_function
        self.publisher = publisher

    def _process(self, msg):
        self._process_function(msg, self.publisher)


class AnnotationDBWorker(QueueWorker):
    def __init__(self, input_queue, process_function, publisher, collection):
        super().__init__(input_queue)
        self.publisher = publisher
        self._process_function = process_function
        self.collection = collection

    def _process(self, msg):
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!")
        self._process_function(msg, self.publisher)