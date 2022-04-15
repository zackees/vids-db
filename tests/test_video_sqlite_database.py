import os
import tempfile
import unittest
from datetime import datetime, timedelta
from typing import List

from vid_db.date import iso_fmt
from vid_db.db_sqlite_video import DbSqliteVideo
from vid_db.video_info import VideoInfo


def test_video_info(url: str = "vid_url0.html") -> VideoInfo:
    """Construct a default video info object."""
    video = VideoInfo.from_dict(
        {
            "channel_name": "XXchannel_name",
            "channel_url": "chann_url0.html",
            "date_published": "2021-02-09 15:22:46.162038-08:00",
            "date_discovered": "2021-02-09 15:22:46.162038-08:00",
            "date_lastupdated": "2021-02-09 15:22:46.162038-08:00",
            "duration": "60",
            "description": "",
            "iframe_src": "1",
            "img_src": "",
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
        tmp_file = tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False)
        tmp_file.close()
        self.cleanup.append(lambda: os.remove(tmp_file.name))
        return os.path.abspath(tmp_file.name)

    def test_add_video_info(self):
        """Adds a video info into the db then tests that it can be found."""
        db_path = self.create_tempfile_path()
        db = DbSqliteVideo(db_path, "table-name")
        video_in: VideoInfo = test_video_info()
        db.insert_or_update(video_in)
        video_in.url = "vid_url1.html"
        db.insert_or_update(video_in)
        videos: List[VideoInfo] = db.find_videos_by_channel_name(channel_name="XXchannel_name")
        self.assertEqual(2, len(videos))

    def test_add_update_video_info(self):
        """Tests that a video can be added and then updated."""
        db_path = self.create_tempfile_path()
        db = DbSqliteVideo(db_path, "table-name")
        video_in: VideoInfo = test_video_info()
        video_in.date_discovered = "2021-02-09T15:00:00.000000-08:00"
        video_in.views = "555"
        db.insert_or_update(video_in)
        # Add the same value one hour later
        video_in.date_discovered = "2021-02-09T16:00:00.000000-08:00"
        video_in.views = "1000"
        db.insert_or_update(video_in)
        vid_out: VideoInfo = db.find_video_by_url(video_in.url)  # type: ignore
        self.assertEqual(iso_fmt(vid_out.date_discovered), "2021-02-09T15:00:00-08:00")
        self.assertEqual(vid_out.views, 1000)

    def test_find_video_by_url(self):
        """Tests that a video can be found by url."""
        db_path = self.create_tempfile_path()
        db = DbSqliteVideo(db_path, "table-name")
        video_in: VideoInfo = test_video_info()
        db.insert_or_update(video_in)
        vid = db.find_video_by_url(video_in.url)
        self.assertEqual(vid, video_in)

    def test_find_video_by_date(self):
        """Tests that a video can be found by date."""
        db_path = self.create_tempfile_path()
        db = DbSqliteVideo(db_path, "table-name")
        video_in: VideoInfo = test_video_info()
        db.insert_or_update(video_in)
        date_start: datetime = video_in.date_published
        date_end: datetime = date_start + timedelta(seconds=1)
        found_vids: List[VideoInfo] = db.find_videos(date_start, date_end)
        self.assertEqual(1, len(found_vids))
        self.assertEqual(found_vids[0], video_in)

    def test_find_video_with_limit(self):
        """Tests that a video can be found and limited by the number of returns."""
        db_path = self.create_tempfile_path()
        db = DbSqliteVideo(db_path, "table-name")
        video_0: VideoInfo = test_video_info("vid_url0.html")
        video_1: VideoInfo = test_video_info("vid_url1.html")
        db.insert_or_update(video_0)
        db.insert_or_update(video_1)
        date_start: datetime = video_0.date_published
        date_end: datetime = date_start + timedelta(seconds=1)
        found_vids: List[VideoInfo] = db.find_videos(date_start, date_end, limit_count=1)
        self.assertEqual(1, len(found_vids))


if __name__ == "__main__":
    unittest.main()
