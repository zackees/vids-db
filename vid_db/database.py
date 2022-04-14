# pylint: disable=all

from datetime import datetime
from typing import List, Optional

from vid_db.db_sqlite_video import DbSqliteVideo  # type: ignore
from vid_db.video_info import VideoInfo


class Database:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.db_videos = DbSqliteVideo(self.db_path, "videos")

    def update_many(self, vids: List[VideoInfo]) -> None:  # type: ignore
        # TODO: Speed up.
        for video in vids:
            self.db_videos.insert_or_update(video)

    def update(self, video_info: VideoInfo) -> None:
        self.db_videos.insert_or_update(video_info)

    def get_video_list(
        self,
        date_start: datetime,
        date_end: datetime,
        channel_name: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[VideoInfo]:
        vid_list: List[VideoInfo] = self.db_videos.find_videos(
            date_start, date_end, channel_name=channel_name, limit_count=limit
        )
        return vid_list
