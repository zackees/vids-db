import time
import unittest

import requests
from vid_db.testing.run_server_in_thread import HOST, PORT, run_server_in_thread

# from vid_db.app import app
from vid_db.version import VERSION


class ApiServerTester(unittest.TestCase):
    """Tester for the ytclip-server."""

    # @unittest.skip("Skip for now")
    def test_platform_executable(self) -> None:
        """Opens up the ytclip-server and tests that the version returned is correct."""
        with run_server_in_thread():
            time.sleep(1)
            version = requests.get(f"http://{HOST}:{PORT}/version").text
            self.assertEqual(VERSION, version)


if __name__ == "__main__":
    unittest.main()
