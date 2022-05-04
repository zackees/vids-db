"""
    Tests whoosh full text search
"""

# pylint: disable=invalid-name,R0801

import shutil
import tempfile
import unittest
from datetime import datetime

from vid_db.database import Database
from vid_db.video_info import VideoInfo


class DatabaseTester(unittest.TestCase):
    """Tester for the Full Search Text Database"""

    def setUp(self) -> None:
        # Create a temporary directory
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        # Remove the temp file.
        shutil.rmtree(self.tempdir)

    def test(self) -> None:
        """Test the full text search database."""
        db = Database(db_path=self.tempdir)
        vid = VideoInfo(
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
        db.update(vid)
        result = db.query_video_list("Red")
        self.assertEqual(1, len(result))
        print(result)

    @unittest.skip("Feature: search by channel name too")
    def test2(self) -> None:
        """Test the full text search database."""
        db = Database(db_path=self.tempdir)
        vid = VideoInfo(
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
        db.update(vid)
        result = db.query_video_list("RedPill78")
        self.assertEqual(1, len(result))


if __name__ == "__main__":
    unittest.main()
