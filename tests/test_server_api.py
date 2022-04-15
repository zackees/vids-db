import os
import time
import unittest
from datetime import datetime

import requests
from vid_db.testing.run_server_in_thread import HOST, PORT, run_server_in_thread
from vid_db.version import VERSION
from vid_db.video_info import VideoInfo

# from vid_db.app import app

# In our testing environment we use the same database for all tests.
HERE = os.path.dirname(os.path.abspath(__file__))
TEST_DB = os.path.join(HERE, "data", "test_vid_db.sqlite")
URL = f"http://{HOST}:{PORT}"


if os.path.exists(TEST_DB):
    os.remove(TEST_DB)

os.environ.update({"VID_DB_FILE": TEST_DB})


def make_vid(channel_name: str, title: str) -> VideoInfo:
    return VideoInfo(
        channel_name=channel_name,
        title=title,
        date_published=datetime.now(),
        date_discovered=datetime.now(),
        date_lastupdated=datetime.now(),
        channel_url=f"{URL}/channel/{channel_name}",
        source="rumble.com",
        url=f"{URL}/video/{title}",
        img_src=f"{URL}/img/{title}.png",
        iframe_src=f"{URL}/iframe/{title}",
        views=100,
        duration=60,
        description="",
    )


class ApiServerTester(unittest.TestCase):
    """Tester for the vid_db."""

    # @unittest.skip("Skip for now")
    def test_platform_executable(self) -> None:
        """Opens up the vid_db and tests that the version returned is correct."""
        with run_server_in_thread():
            time.sleep(1)
            version = requests.get(f"{URL}/version").text
            self.assertEqual(VERSION, version)

    # @unittest.skip("Skip for now")
    def test_platform_put_get(self) -> None:
        """Opens up the vid_db and tests that the version returned is correct."""
        with run_server_in_thread():
            time.sleep(1)
            vid = make_vid("test_channel", "test_title")
            r = requests.put(f"{URL}/put/video", json=vid.to_dict())
            r.raise_for_status()
            r = requests.get(f"{URL}/feed/hours/1")
            r.raise_for_status()
            data = r.json()
            self.assertEqual(1, len(data))
            v = VideoInfo(**data[0])
            self.assertEqual("test_title", v.title)


if __name__ == "__main__":
    unittest.main()
