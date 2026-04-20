import threading
import time
from queue import Queue

# Shared queue for "incoming messages"
message_queue = Queue()


def worker_task():
    """Main task: add 2, then wait 10 seconds"""
    x = 0
    while True:
        x += 2
        print(f"[WORKER] Value is now: {x}")
        time.sleep(1)  # simulate long blocking work


def listener_task():
    """Listener thread: checks for messages without blocking everything else"""
    while True:
        if not message_queue.empty():
            msg = message_queue.get()
            print(f"[LISTENER] Received message: {msg}")
        time.sleep(1)  # rate limiting a polling loop


def simulate_incoming_messages():
    """Simulates external messages arriving"""
    count = 1
    while True:
        time.sleep(5)
        message = f"message_{count}"
        print(f"[SIMULATOR] Adding {message}")
        message_queue.put(message)
        count += 1


if __name__ == "__main__":
    # Create threads: if daemon=False (default), thread must finish before program exits
    # That function runs independently of the main thread
    # Threads are not fully independent — they share: memory, variables, state
    worker_thread = threading.Thread(target=worker_task, daemon=True)
    listener_thread = threading.Thread(target=listener_task, daemon=True)
    simulator_thread = threading.Thread(target=simulate_incoming_messages, daemon=True)

    # Start threads
    worker_thread.start()
    listener_thread.start()
    simulator_thread.start()

    # Keep main thread alive: If main thread exits → program exits → all threads die
    while True:
        time.sleep(1)