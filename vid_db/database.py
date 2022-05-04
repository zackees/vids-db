# pylint: disable=all
import os
from datetime import datetime
from typing import List, Optional

from vid_db.db_full_text_search import DbFullTextSearch
from vid_db.db_sqlite_video import DbSqliteVideo  # type: ignore
from vid_db.video_info import VideoInfo

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH_DIR = os.path.join(HERE, "data")
DB_PATH_FTS = os.path.join(DB_PATH_DIR, "full_text_seach")
DB_PATH_SQLITE = os.path.join(DB_PATH_DIR, "videos.sqlite")
os.makedirs(DB_PATH_DIR, exist_ok=True)


class Database:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.db_sqlite = DbSqliteVideo(DB_PATH_SQLITE)
        self.db_full_text_search = DbFullTextSearch(DB_PATH_FTS)

    def update_many(self, vids: List[VideoInfo]) -> None:  # type: ignore
        # TODO: Speed up.
        self.db_sqlite.insert_or_update(vids)
        self.db_full_text_search.add_videos(vids)

    def update(self, vid: VideoInfo) -> None:
        self.update_many([vid])

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

    def query_video_list(
        self,
        query_string: str,
        limit: Optional[int] = None,
    ) -> List[dict]:
        options = {}
        if limit is not None:
            options["limit"] = limit
        vid_list: List[dict] = self.db_full_text_search.title_search(
            query_string, **options
        )
        return vid_list
