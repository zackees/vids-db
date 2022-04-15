# type: ignore


import contextlib
import threading
import time

import uvicorn
from uvicorn.config import Config

APP_NAME = "vid_db.app:app"
HOST = "127.0.0.1"
PORT = 4422  # Arbitrarily chosen.


# Surprisingly uvicorn does allow graceful shutdowns, making testing hard.
# This class is the stack overflow answer to work around this limitiation.
# Note: Running this in python 3.8 and below will cause the console to spew
# scary warnings during test runs:
#   ValueError: set_wakeup_fd only works in main thread
class ServerWithShutdown(uvicorn.Server):
    """Adds a shutdown method to the uvicorn server."""

    def install_signal_handlers(self):
        pass


@contextlib.contextmanager
def run_server_in_thread():
    """
    Useful for testing, this function brings up a server.
    It's a context manager so that it can be used in a with statement.
    """
    config = Config(APP_NAME, host=HOST, port=PORT, log_level="info", use_colors=False)
    server = ServerWithShutdown(config=config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    try:
        while not server.started:
            time.sleep(1e-3)
        yield
    finally:
        server.should_exit = True
        thread.join()
