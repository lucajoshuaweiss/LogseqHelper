"""
Background task helpers.
"""

import threading
from concurrent.futures import ThreadPoolExecutor


def run_in_thread(func):
    thread = threading.Thread(target=func)
    thread.daemon = True
    thread.start()

class ThreadedExecutor:
    def __init__(self, max_workers=8):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def submit_task(self, func, *args):
        self.executor.submit(func, *args)

    def shutdown(self):
        self.executor.shutdown()