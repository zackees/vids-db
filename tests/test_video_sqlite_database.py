"""
Tests the sqlite video database
"""

# pylint: disable=invalid-name

import os
import tempfile
import unittest
from datetime import datetime, timedelta
from typing import List

from vids_db.db_sqlite_video import DbSqliteVideo
from vids_db.models import Video


def test_video_info(url: str = "http://example.com/vid_url0.html") -> Video:
    """Construct a default video info object."""
    video = Video(
        **{
            "channel_name": "XXchannel_name",
            "channel_url": "https://chann_url0.html",
            "date_published": "2021-02-09 15:22:46.162038-08:00",
            "date_lastupdated": "2021-02-09 15:22:46.162038-08:00",
            "duration": "60",
            "description": "",
            "iframe_src": "http://example.com/iframe_url0.html",
            "img_src": "http://img_src0.jpg",
            "profile_img_src": "",
            "source": "rumble.com",
            "title": "Vid0",
            "url": url,
            "views": "913",
        }
    )
    return video


class DbSqliteVideoTester(unittest.TestCase):
    """Tests the functionality of the sqlite database"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cleanup = []

    def tearDown(self):
        for cleanup in self.cleanup:
            try:
                cleanup()
            except Exception as exc:  # pylint: disable=broad-except
                print(str(exc))
        self.cleanup = []

    def create_tempfile_path(self) -> str:
        """Creates a temporary file that will be deleted when the test is complete."""
        tmp_file = (
            tempfile.NamedTemporaryFile(  # pylint: disable=consider-using-with
                suffix=".sqlite3", delete=False
            )
        )
        tmp_file.close()
        self.cleanup.append(lambda: os.remove(tmp_file.name))
        return os.path.abspath(tmp_file.name)

    def test_add_video_info(self):
        """Adds a video info into the db then tests that it can be found."""
        db_path = self.create_tempfile_path()
        db = DbSqliteVideo(db_path)
        video_in: Video = test_video_info()
        db.insert_or_update([video_in])
        video_in.url = "http://example.com/vid_url1.html"
        db.insert_or_update([video_in])
        videos: List[Video] = db.find_videos_by_channel_name(
            channel_name="XXchannel_name"
        )
        self.assertEqual(2, len(videos))

    def test_add_update_video_info(self):
        """Tests that a video can be added and then updated."""
        db_path = self.create_tempfile_path()
        db = DbSqliteVideo(db_path)
        video_in: Video = test_video_info()
        video_in.views = "555"
        db.insert_or_update([video_in])
        # Add the same value one hour later
        video_in.views = "1000"
        db.insert_or_update([video_in])
        vid_out: Video = db.find_video_by_url(video_in.url)  # type: ignore
        self.assertEqual(vid_out.views, 1000)

    def test_find_video_by_url(self):
        """Tests that a video can be found by url."""
        db_path = self.create_tempfile_path()
        db = DbSqliteVideo(db_path)
        video_in: Video = test_video_info()
        db.insert_or_update([video_in])
        vid = db.find_video_by_url(video_in.url)
        self.assertEqual(vid, video_in)

    def test_find_vides_by_urls(self):
        """Tests that two videos can be found by url."""
        db_path = self.create_tempfile_path()
        db = DbSqliteVideo(db_path)
        vids = [
            test_video_info(url="http://example.com/a"),
            test_video_info(url="http://example.com/b"),
        ]
        db.insert_or_update(vids)
        vids = db.find_videos_by_urls(
            ["http://example.com/a", "http://example.com/b"]
        )
        self.assertEqual(2, len(vids))

    def test_find_video_by_date(self):
        """Tests that a video can be found by date."""
        db_path = self.create_tempfile_path()
        db = DbSqliteVideo(db_path)
        video_in: Video = test_video_info()
        db.insert_or_update([video_in])
        date_start: datetime = video_in.date_published
        date_end: datetime = date_start + timedelta(seconds=1)
        found_vids: List[Video] = db.find_videos(date_start, date_end)
        self.assertEqual(1, len(found_vids))
        self.assertEqual(found_vids[0], video_in)

    def test_find_video_with_limit(self):
        """Tests that a video can be found and limited by the number of returns."""
        db_path = self.create_tempfile_path()
        db = DbSqliteVideo(db_path)
        video_0: Video = test_video_info("https://example.com/vid_url0.html")
        video_1: Video = test_video_info("https://example.com/vid_url1.html")
        db.insert_or_update([video_0, video_1])
        date_start: datetime = video_0.date_published
        date_end: datetime = date_start + timedelta(seconds=1)
        found_vids: List[Video] = db.find_videos(
            date_start, date_end, limit_count=1
        )
        self.assertEqual(1, len(found_vids))

    def test_get_channel_names(self):
        """Tests that a video can be found and limited by the number of returns."""
        db_path = self.create_tempfile_path()
        db = DbSqliteVideo(db_path)
        video_0: Video = test_video_info("https://example.com/vid_url0.html")
        video_1: Video = test_video_info("https://example.com/vid_url1.html")
        db.insert_or_update([video_0, video_1])
        channel_names = db.get_channel_names()
        self.assertEqual(1, len(channel_names))


if __name__ == "__main__":
    unittest.main()
