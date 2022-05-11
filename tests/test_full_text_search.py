"""
    Tests whoosh full text search
"""

# pylint: disable=invalid-name,R0801,line-too-long
import atexit
import os
import shutil
import tempfile
import unittest
from datetime import datetime

from vids_db.db_full_text_search import DbFullTextSearch
from vids_db.models import Video


class DbFullTextSearchTester(unittest.TestCase):
    """Tester for the Full Search Text Database"""

    def setUp(self) -> None:
        # Create a temporary directory
        self.tempdir = tempfile.mkdtemp()
        clean_fcn = lambda: shutil.rmtree(self.tempdir, ignore_errors=True)
        atexit.register(clean_fcn)

    def test_title_search(self) -> None:
        """Test the full text search database."""
        db = DbFullTextSearch(index_path=self.tempdir)
        self.assertTrue(os.listdir(self.tempdir))
        vid = Video(
            channel_name="RedPill78",
            title="TheRedPill",
            date_published=datetime.now(),
            date_lastupdated=datetime.now(),
            channel_url="https://www.youtube.com/channel/UC-9-kyTW8ZkZNDHQJ6FgpwQ",
            source="youtube",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            duration="60",
            description="A cool video",
            img_src="https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
            iframe_src="https://www.youtube.com/embed/dQw4w9WgXcQ",
            views=1,
        )
        db.add_videos([vid])
        out = db.title_search("Red")
        self.assertEqual(1, len(out))

        out = db.title_search("Red Pill")
        self.assertEqual(1, len(out))

    def test_date_range_search(self) -> None:
        """Test the full text search database."""
        db = DbFullTextSearch(index_path=self.tempdir)
        self.assertTrue(os.listdir(self.tempdir))
        vid = Video(
            channel_name="RedPill78",
            title="TheRedPill",
            date_published=datetime.now(),
            date_lastupdated=datetime.now(),
            channel_url="https://www.youtube.com/channel/UC-9-kyTW8ZkZNDHQJ6FgpwQ",
            source="youtube",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            duration="60",
            description="A cool video",
            img_src="https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
            iframe_src="https://www.youtube.com/embed/dQw4w9WgXcQ",
            views=1,
        )
        db.add_videos([vid])
        out = db.title_search("Red Pill date:a week ago")
        self.assertEqual(0, len(out))

        out = db.title_search("Red Pill date:today")
        self.assertEqual(1, len(out))

    def test_double_add(self) -> None:
        """
        Tests that videos can be added twice but they will
        only exist once in the database.
        """
        db = DbFullTextSearch(index_path=self.tempdir)
        self.assertTrue(os.listdir(self.tempdir))
        vid = Video(
            channel_name="RedPill78",
            title="TheRedPill",
            date_published=datetime.now(),
            date_lastupdated=datetime.now(),
            channel_url="https://www.youtube.com/channel/UC-9-kyTW8ZkZNDHQJ6FgpwQ",
            source="youtube",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            duration="60",
            description="A cool video",
            img_src="https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
            iframe_src="https://www.youtube.com/embed/dQw4w9WgXcQ",
            views=1,
        )
        db.add_videos([vid])
        db.add_videos([vid])
        out = db.title_search("Red")
        self.assertEqual(1, len(out))

    def test_double_add2(self) -> None:
        """
        Tests that the videos can be added in the same batch and
        only exist once in the database.
        """
        db = DbFullTextSearch(index_path=self.tempdir)
        self.assertTrue(os.listdir(self.tempdir))
        vid = Video(
            channel_name="RedPill78",
            title="TheRedPill",
            date_published=datetime.now(),
            date_lastupdated=datetime.now(),
            channel_url="https://www.youtube.com/channel/UC-9-kyTW8ZkZNDHQJ6FgpwQ",
            source="youtube",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            duration="60",
            description="A cool video",
            img_src="https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
            iframe_src="https://www.youtube.com/embed/dQw4w9WgXcQ",
            views=1,
        )
        db.add_videos([vid, vid])
        out = db.title_search("Red")
        self.assertEqual(1, len(out))

    def test_bug(self) -> None:
        """Tests bug where redpill would not match."""
        db = DbFullTextSearch(index_path=self.tempdir)
        vid = Video(
            channel_name="Nicholas Veniamin",
            title="Melissa Redpill Discusses Supreme Court To Overturn Abortion Law with Nicholas Veniamin",
            date_published="2022-05-04T05:25:14+00:00",
            date_discovered="2022-05-03T22:39:32.373630-07:00",
            date_lastupdated="2022-05-06T19:40:42.227151-07:00",
            channel_url="https://www.bitchute.com/channel/jcOs2EA1BUJH/",
            source="bitchute.com",
            url="https://www.bitchute.com/video/zmZMfRiguhuf",
            duration="29:57",
            description="",
            img_src="https://static-3.bitchute.com/live/cover_images/jcOs2EA1BUJH/zmZMfRiguhuf_640x360.jpg",
            iframe_src="https://www.bitchute.com/embed/zmZMfRiguhuf",
            views="4958",
        )
        db.add_videos([vid])
        out = db.title_search("RedPill")
        self.assertEqual(1, len(out))


if __name__ == "__main__":
    unittest.main()
