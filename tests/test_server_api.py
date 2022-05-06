"""
Tests the fastapi server.
"""

# pylint: disable=invalid-name,R0801

import os
import shutil
import time
import unittest
from datetime import datetime

import requests  # type: ignore
from vid_db.models import Video
from vid_db.testing.run_server_in_thread import (  # type: ignore
    HOST,
    PORT,
    run_server_in_thread,
)
from vid_db.version import VERSION

# In our testing environment we use the same database for all tests.
HERE = os.path.dirname(os.path.abspath(__file__))
TEST_DB = os.path.join(HERE, "data")
URL = f"http://{HOST}:{PORT}"


if os.path.exists(TEST_DB):
    shutil.rmtree(TEST_DB, ignore_errors=True)

os.environ.update({"VID_DB_FILE": TEST_DB})


def make_vid(channel_name: str, title: str) -> Video:
    """Generates a video with default values."""
    return Video(
        channel_name=channel_name,
        title=title,
        date_published=datetime.now(),
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
    def test_platform_put_get(self) -> None:  # pylint: disable=no-self-use
        """Opens up the vid_db and tests that the version returned is correct."""
        with run_server_in_thread():
            time.sleep(1)
            vid = make_vid("test_channel", "test_title")
            r = requests.put(f"{URL}/put/video", json=vid.to_json())
            r.raise_for_status()
            r = requests.get(f"{URL}/rss/all?hours_ago=24")
            r.raise_for_status()
            # data = r.json()
            # self.assertEqual(1, len(data))
            # v = VideoInfo(**data[0])
            # self.assertEqual("test_title", v.title)


if __name__ == "__main__":
    unittest.main()
