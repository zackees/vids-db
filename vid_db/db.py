# pylint: disable=all

import json
from datetime import datetime
from typing import List, Optional

from keyvalue_sqlite import KeyValueSqlite as KeyValueDB  # type: ignore

from db_sqlite_video import DbSqliteVideo  # type: ignore
from vid_db.video_info import VideoInfo

DB_VIDEOAGG = ":memory:"

TABLE_BLAST_VIDEO_SETTINGS = "BLAST-VIDEO-SETTINGS"
TABLE_BLAST_VIDEO_ARTICLE_DB = "TABLE-BLAST-VIDEO-ARTICLE-DB"

DATABASE_VERSION_001_IMAGE_SIZES = 1
DATABASE_VERSION = DATABASE_VERSION_001_IMAGE_SIZES

# TODO: Drop this table programmatically.
# TABLE_BLAST_VIDEO_CHANNEL_HISTORY = 'BLAST-VIDEO-CHANNEL-HISTORY'


# so snapshot comes in
# and the parts get broken down into
#  A) data
#  B) content
# How do we define "popularity"
# For each influencer:
#   get the last 20 videos
#     each having #number of views
#   check their median value for views
#     amplify those with a very high leap on a certain video

# But to do that we are going to need a different database.
# src_url (indexed) | date_first_detected (indexed) |
# Just stuff a json dictionary into every influencer. This is fine.
# "InfoWars" -> dict{...}


def filter_by_inclusion_list(vids: List[VideoInfo]) -> List[VideoInfo]:
    """Any video author that is not in the CHANNEL_LIBRARY is excluded."""
    # DISABLED
    #    channel_name_set = set([d[0] for d in CHANNEL_LIBRARY])
    #    out: List[VideoInfo] = [v for v in vids if v.channel_name in channel_name_set]
    #    return out
    return vids


def filter_by_channel_list(vids: List[VideoInfo], channel_list: List[str]) -> List[VideoInfo]:
    filtered: List[VideoInfo] = [v for v in vids if v.channel_name in channel_list]
    return filtered


class Database:
    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = db_path or DB_VIDEOAGG
        self.db_settings = KeyValueDB(self.db_path, TABLE_BLAST_VIDEO_SETTINGS)
        self.db_videos = DbSqliteVideo(self.db_path, TABLE_BLAST_VIDEO_ARTICLE_DB)

    def add_snapshot(self, data_json) -> None:  # type: ignore
        content = json.loads(data_json)
        # Now that default timestamps have been set, putt them back out of the database and
        # use them for the stored json.
        for video in content:
            self.db_videos.insert_or_update(VideoInfo.from_dict(video))

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
