"""
    Tests whoosh full text search
"""

import shutil
import tempfile
import unittest
from datetime import datetime
from typing import Any, List

from vid_db.video_info import VideoInfo
from whoosh import fields, query
from whoosh.analysis import FancyAnalyzer
from whoosh.compat import u
from whoosh.filedb.filestore import FileStorage

SCHEMA = fields.Schema(
    url=fields.ID(stored=True, unique=True, sortable=True),
    channel_name=fields.TEXT(stored=True, sortable=True),
    published=fields.DATETIME(stored=True, sortable=True),
    title=fields.TEXT(stored=True, analyzer=FancyAnalyzer()),
)

CHANNEL_NAME = "RedPill78"


def urls(results):
    return sorted([fields["url"] for fields in results])


class FullTextSearchDb:
    def __init__(self, index_path) -> None:
        self.storage = FileStorage(index_path)
        if self.storage.index_exists():
            self.index = self.storage.open_index()
        else:
            self.index = self.storage.create_index(SCHEMA)

    def add_videos(self, videos: List[VideoInfo]) -> None:
        with self.index.writer() as writer:
            with writer.group():
                for vid in videos:
                    published: datetime = vid.date_published
                    writer.add_document(
                        url=vid.url,
                        channel_name=u(vid.channel_name),
                        published=published,
                        title=u(vid.title),
                    )

    def title_search(self, query_string: str) -> List[Any]:
        assert query_string == query_string.lower()
        with self.index.searcher() as s:
            q = query.Phrase("title", [u(query_string)])
            m = q.matcher(s)
            assert m.__class__.__name__ == "SpanNear2Matcher"
            results = s.search(q)
            urls = sorted([fields["url"] for fields in results])
            return urls


class FullTextSearchDbTester(unittest.TestCase):
    def setUp(self) -> None:
        # Create a temporary directory
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        # Remove the temp file.
        shutil.rmtree(self.tempdir)

    def test(self) -> None:
        db = FullTextSearchDb(index_path=self.tempdir)
        vid = VideoInfo(
            channel_name=CHANNEL_NAME,
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
        out = db.title_search("red")
        self.assertEqual(1, len(out))


if __name__ == "__main__":
    unittest.main()
