# pylint: disable=all
import os
from datetime import datetime
from typing import List, Optional

from vid_db.db_full_text_search import FullTextSearchDb
from vid_db.db_sqlite_video import DbSqliteVideo  # type: ignore
from vid_db.video_info import VideoInfo

DB_SQLITE_TABLE_NAME = "videos"
HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH_DIR = os.path.join(HERE, "data")
DB_PATH_FTS = os.path.join(DB_PATH_DIR, "full_text_seach")
DB_PATH_SQLITE = os.path.join(DB_PATH_DIR, "videos.sqlite")
os.makedirs(DB_PATH_DIR, exist_ok=True)


class Database:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.db_sqlite = DbSqliteVideo(DB_PATH_SQLITE, DB_SQLITE_TABLE_NAME)
        self.db_full_text_search = FullTextSearchDb(DB_PATH_FTS)

    def update_many(self, vids: List[VideoInfo]) -> None:  # type: ignore
        # TODO: Speed up.
        self.db_sqlite.insert_or_update(vids)
        self.db_full_text_search.add_videos(vids)

    def update(self, vid: VideoInfo) -> None:
        self.db_sqlite.insert_or_update([vid])

    def get_video_list(
        self,
        date_start: datetime,
        date_end: datetime,
        channel_name: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[VideoInfo]:
        vid_list: List[VideoInfo] = self.db_sqlite.find_videos(
            date_start, date_end, channel_name=channel_name, limit_count=limit
        )
        return vid_list
