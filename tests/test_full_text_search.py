"""
    Tests whoosh full text search
"""

import shutil
import tempfile
import unittest
from datetime import datetime

from vid_db.db_full_text_search import FullTextSearchDb
from vid_db.video_info import VideoInfo


class FullTextSearchDbTester(unittest.TestCase):
    """Tester for the Full Search Text Database"""

    def setUp(self) -> None:
        # Create a temporary directory
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        # Remove the temp file.
        shutil.rmtree(self.tempdir)

    def test(self) -> None:
        db = FullTextSearchDb(index_path=self.tempdir)
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
        db.add_videos([vid])
        out = db.title_search("Red")
        self.assertEqual(1, len(out))

        out = db.title_search("Red Pill")
        self.assertEqual(1, len(out))

        out = db.title_search("Red Pill published:a week ago")
        self.assertEqual(0, len(out))

        out = db.title_search("Red Pill published:today")
        self.assertEqual(1, len(out))


if __name__ == "__main__":
    unittest.main()
