"""
    Tests whoosh full text search
"""

# pylint: disable=invalid-name,R0801

import json
import os
import shutil
import tempfile
import unittest

from vids_db.database import Database
from vids_db.models import Video

# from vids_db.models import Video

HERE = os.path.dirname(os.path.abspath(__file__))
TEST_DATA = os.path.join(HERE, "test_data.json")


def convert(video_json: dict) -> Video:
    """
    Converts a video json to a video object
    """
    views = video_json["views"]
    channel_url = video_json["channel_url"]
    if views == "?" or views == "":
        views = 0
    else:
        views = int(views)
    try:
        video = Video(
            channel_name=video_json["channel_name"],
            title=video_json["title"],
            date_published=video_json["date_published"],
            date_lastupdated=video_json["date_lastupdated"],
            channel_url=channel_url,
            source=video_json["source"],
            url=video_json["url"],
            duration=video_json["duration"],
            description=video_json["description"],
            img_src=video_json["img_src"],
            iframe_src=video_json["iframe_src"],
            views=int(views),
        )
    except ValueError as verr:
        print(f"ValueError: {verr}")
    return video


class DatabaseStressTester(unittest.TestCase):
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
        with open(TEST_DATA, encoding="utf-8", mode="r") as f:
            json_data = json.loads(f.read())
        vids = []
        for video in json_data["content"]:
            vids.append(convert(video))
        db.update_many(vids)
        result = db.query_video_list("biden")
        print(len(result))


if __name__ == "__main__":
    unittest.main()
