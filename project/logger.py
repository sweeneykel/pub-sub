import logging

def make_logger():
    # move to main to configure for all modules
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(threadName)s] %(message)s"
    )
    # creates a logger named after module
    logger = logging.getLogger(__name__)
    return logger