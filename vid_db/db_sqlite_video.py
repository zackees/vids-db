# pylint: disable=all

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

from vid_db.date import parse_date_to_unix_utc
from vid_db.video_info import VideoInfo


class DbSqliteVideo:
    """SQLite3 context manager"""

    def __init__(self, db_path: str, table_name: str) -> None:
        self.db_path = db_path
        folder_path = os.path.dirname(self.db_path)
        os.makedirs(folder_path, exist_ok=True)
        self.table_name = table_name.replace("-", "_")
        if self.db_path == "" or self.db_path == ":memory:":
            raise ValueError("Can not use in memory database for DbSqliteVideo")
        self.create_table()

    def create_table(self) -> None:
        with self.open_db_for_write() as conn:
            # Check to see if it's exists first of all.
            check_table_stmt = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.table_name}';"
            cursor = conn.execute(check_table_stmt)
            has_table = cursor.fetchall()
            if has_table:
                return
        create_stmt = [
            "PRAGMA journal_mode=wal2;",
            f"CREATE TABLE {self.table_name} (",
            "   url TEXT PRIMARY KEY UNIQUE NOT NULL,",
            "   channel_name TEXT,",
            "   timestamp_published INT,",
            "   data TEXT);",
            f"CREATE INDEX index_channel_name ON {self.table_name}(channel_name);",
            f"CREATE INDEX timestamp_published ON {self.table_name}(channel_name);",
        ]
        create_stmt_str: str = "\n".join(create_stmt)
        with self.open_db_for_write() as conn:
            try:
                conn.executescript(create_stmt_str)
            except sqlite3.ProgrammingError:
                pass  # Table already created

    @contextmanager
    def open_db_for_write(self):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
        except sqlite3.OperationalError as e:
            raise OSError(
                "Error while opening %s\nOriginal Error: %s" % (self.db_path, e)
            )
        try:
            yield conn
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @contextmanager
    def open_db_for_read(self):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=10)
        except sqlite3.OperationalError as e:
            raise OSError(
                "Error while opening %s\nOriginal Error: %s" % (self.db_path, e)
            )
        try:
            yield conn
        finally:
            conn.close()

    def _insert_or_replace(self, video_info: VideoInfo) -> None:
        channel_name = video_info.channel_name
        url = video_info.url
        timestamp_published = int(parse_date_to_unix_utc(video_info.date_published))
        insert_stmt = [
            f"INSERT OR REPLACE INTO {self.table_name} (",
            "    url,",
            "    channel_name,",
            "    timestamp_published,",
            "    data",
            ") VALUES (?, ?, ?, ?)",
        ]
        insert_stmt_cmd = "\n".join(insert_stmt)
        json_data = json.dumps(video_info.to_dict(), ensure_ascii=False)
        record = (
            url,
            channel_name,
            timestamp_published,
            json_data,
        )
        with self.open_db_for_write() as conn:
            conn.execute(insert_stmt_cmd, record)
            conn.commit()

    def insert_or_update(self, vid_in: VideoInfo) -> None:
        vid: Optional[VideoInfo]
        vid = self.find_video_by_url(vid_in.url)
        if vid:
            vid_in.date_discovered = vid.date_discovered
        self._insert_or_replace(vid_in)

    def find_videos_by_channel_name(self, channel_name: str) -> List[VideoInfo]:
        select_stmt = "SELECT data FROM %s WHERE channel_name=(?)" % self.table_name
        output: List[str] = []
        with self.open_db_for_read() as conn:
            cursor = conn.execute(select_stmt, (channel_name,))
            for row in cursor:
                output.append(row[0])
        return [VideoInfo.from_dict(json.loads(s)) for s in output]

    def find_video_by_url(self, url: str) -> Optional[VideoInfo]:
        select_stmt = "SELECT data FROM %s WHERE url=(?)" % self.table_name
        with self.open_db_for_read() as conn:
            cursor = conn.execute(select_stmt, (url,))
            for row in cursor:
                data: Dict = json.loads(row[0])
                out: VideoInfo = VideoInfo.from_dict(data)
                return out
        return None

    def find_videos(
        self,
        date_start: datetime,
        date_end: datetime,
        channel_name: Optional[str] = None,
        limit_count: Optional[int] = None,
    ) -> List[VideoInfo]:
        output: List[VideoInfo] = []
        from_time = int(date_start.timestamp())
        to_time = int(date_end.timestamp())
        if limit_count is not None:
            limit_clause = f"LIMIT {limit_count}"
        else:
            limit_clause = ""
        if channel_name is None:
            select_stmt = f"SELECT data FROM {self.table_name} WHERE timestamp_published BETWEEN ? AND ? ORDER BY timestamp_published DESC {limit_clause};"
            values = (from_time, to_time)  # type: ignore
        else:
            select_stmt = (
                f"SELECT data FROM {self.table_name} WHERE channel_name=(?) and"
                " timestamp_published BETWEEN ? AND ?"
                f" ORDER BY timestamp_published DESC {limit_clause};"
            )
            values = (channel_name, from_time, to_time)  # type: ignore
        with self.open_db_for_read() as conn:  # TODO: have a read-mode.
            cursor = conn.execute(select_stmt, values)
            all_rows = cursor.fetchall()
        for row in all_rows:
            json_data = row[0]
            data = json.loads(json_data)
            vid = VideoInfo.from_dict(data)
            output.append(vid)
        return output

    def get_all_videos(self) -> List[VideoInfo]:
        select_stmt = f"SELECT data FROM {self.table_name}"
        output: List[str] = []
        with self.open_db_for_read() as conn:
            cursor = conn.execute(select_stmt)
            for row in cursor:
                output.append(row[0])
        return [VideoInfo.from_json_str(s) for s in output]

    def to_data(self) -> List[Any]:
        out = []
        select_stmt = f"SELECT * FROM {self.table_name}"
        with self.open_db_for_read() as conn:
            cursor = conn.execute(select_stmt)
            for row in cursor:
                values = list(row)  # Copy
                out.append(values)
        return out
