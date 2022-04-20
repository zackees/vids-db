import unittest
from datetime import datetime

import feedparser
from vid_db.rss import from_rss, to_rss
from vid_db.video_info import VideoInfo

# from vid_db.app import app

URL = "http://localhost"


def make_vid(channel_name: str, title: str) -> VideoInfo:
    """Generates a video with default values."""
    return VideoInfo(
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
        description="test description",
    )


class RssTester(unittest.TestCase):
    """Tests the functionality of the rss algorithm."""

    def test_to_rss(self) -> None:
        """Tests the serialization back and forth between Video and rss"""
        vidlist = [
            make_vid("test_channel", "test_title"),
            make_vid("test_channel2", "test_title2"),
        ]
        rss = to_rss(vidlist)
        parsed = feedparser.parse(rss)
        self.assertEqual(2, len(parsed.entries))
        self.assertEqual("AllVids", parsed.feed.title)
        entry = parsed.entries[0]
        self.assertEqual("test_channel", entry.channel_name)
        self.assertEqual("test_title", entry.title)
        self.assertEqual("http://localhost/channel/test_channel", entry.channel_url)
        self.assertEqual("test description", entry.description)
        self.assertEqual("100", entry.views)
        self.assertEqual("60", entry.duration)
        self.assertEqual("rumble.com", entry.host)
        self.assertIn(URL, entry.url)
        self.assertIn(URL, entry.iframe)
        self.assertIn(URL, entry.thumbnail)

    def test_from_rss(self) -> None:
        """Tests the serialization back and forth between Video and rss"""
        vidlist = [
            make_vid("test_channel", "test_title"),
            make_vid("test_channel2", "test_title2"),
        ]
        rss = to_rss(vidlist)
        vidlist = from_rss(rss)
        self.assertEqual(2, len(vidlist))


if __name__ == "__main__":
    unittest.main()
