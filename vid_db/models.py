# disable pylint for the entire file
# pylint: disable=all

from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse

from pydantic import (
    AnyUrl,
    BaseModel,
    ConstrainedStr,
    NonNegativeInt,
    validator,
)

from vid_db.date import iso_fmt, now_local, parse_datetime


def check_url(url: str) -> None:
    """
    Checks that the url is in the format https://...
    """
    _ = urlparse(url)


def check_duration(duration: str) -> None:
    """
    Checks that the duration is in the format HH:MM:SS.
    Other acceptable formats include SS.
    Ok:
      ""
      "?"
      06
      6
      60
      61
      23:24
      23:24:01.34
    Not Ok:
      -7
      61  # above 60 seconds
      61:01 # above 60 minutes
      25:24:01.34 # above 24 hours
    """

    def _raise() -> None:
        raise ValueError(f"Invalid duration: {duration}")

    if "" == duration or "?" == duration:
        return
    # Simple case
    if ":" not in duration and "." not in duration:
        try:
            tmp = int(duration)
            if tmp < 0:
                _raise()
            return
        except ValueError:
            _raise()
    new_duration = duration
    if "." in new_duration:
        new_duration = new_duration.split(".")[0]
    units = new_duration.split(":")
    units.reverse()
    if len(units) > 3 or len(units) < 1:
        _raise()
    if not units[0].isnumeric():
        _raise()
    tmp = int(units[0])
    if tmp >= 60 or tmp < 0:
        _raise()
    if len(units) == 1:
        return
    if not units[1].isnumeric():
        _raise()
    tmp = int(units[1])
    if tmp >= 60 or tmp < 0:
        _raise()
    if len(units) == 2:
        return
    if not units[2].isnumeric():
        _raise()
    tmp = int(units[2])
    if tmp >= 24 or tmp < 0:
        _raise()
    if len(units) == 3:
        return
    _raise()


class Video(BaseModel):
    """Represents a video object."""

    channel_name: ConstrainedStr
    title: ConstrainedStr
    date_published: datetime  # from the scraped website
    date_lastupdated: datetime
    channel_url: AnyUrl
    source: ConstrainedStr
    url: AnyUrl
    duration: str
    description: ConstrainedStr
    img_src: AnyUrl
    iframe_src: ConstrainedStr
    views: NonNegativeInt
    # rank: Optional[float] = None  # optional stdev rank.

    @validator("duration")
    def check_duration(cls, v):
        check_duration(v)
        return v

    @validator("views")
    def check_views(cls, v):
        if v == "":
            return v
        if int(v) < 0:
            raise ValueError(f"Invalid views: {v}")
        return v

    @validator("channel_name")
    def check_channel_name(cls, v):
        if not v:
            raise ValueError(f"Invalid channel_name: {v}")
        return v

    def to_dict(self) -> Dict:
        """Generates a dictionary representing this class instance."""
        out = {
            "channel_name": self.channel_name,
            "title": self.title,
            "date_published": iso_fmt(self.date_published),
            "date_lastupdated": iso_fmt(self.date_lastupdated),
            "channel_url": self.channel_url,
            "source": self.source,
            "url": self.url,
            "duration": self.duration,
            "description": self.description,
            "img_src": self.img_src,
            "iframe_src": self.iframe_src,
            "views": self.views,
        }
        return out

    @classmethod
    def from_json_str(cls, data: str) -> Video:
        """Deserializes from dictionary json str back to VideoInfo"""
        d = json.loads(data)
        return Video.from_dict(d)

    @classmethod
    def from_dict(cls, data: Dict) -> Video:
        """Deserializes from dictionary back to VideoInfo"""
        views = parse_views(data["views"])
        return Video(
            channel_name=data["channel_name"],
            title=data["title"],
            date_published=parse_datetime(data["date_published"]),
            date_lastupdated=parse_datetime(data["date_lastupdated"]),
            channel_url=data["channel_url"],
            source=data["source"],
            url=data["url"],
            duration=data["duration"],
            description=data["description"],
            img_src=data["img_src"],
            # img_width, img_height, status were added recently, and therefore are optional.
            iframe_src=data["iframe_src"],
            views=views,
        )

    @classmethod
    def from_list_of_dicts(cls, data: List[Dict]) -> List[Video]:
        out: List[Video] = []
        for datum in data:
            vid = Video.from_dict(datum)
            out.append(vid)
        return out

    @classmethod
    def to_plain_list(cls, data: List[Video]) -> List[Dict]:
        out = []
        vid_info: Video
        for vid_info in data:
            d = vid_info.to_dict()
            out.append(d)
        return out

    @classmethod
    def to_compact_csv(
        cls, vid_list: List[Video], exclude_columns: Optional[Set[str]] = None
    ) -> List[List]:
        """
        Generates a compact csv form of the data. The csv form consists of a header list, followed by N data
        lists. This has the advantage of eliminating the redundant keys in the dictionary form, which helps
        reduce the size of the file over the wire.
        """
        columns_set: Set[str] = set({})
        for vid in vid_list:
            vid_dict = vid.to_dict()
            for key in vid_dict.keys():
                columns_set.add(key)
        if exclude_columns:
            columns_set = columns_set - exclude_columns
        exclude_columns = exclude_columns or set({})
        columns = sorted(list(columns_set))
        out: List[Any] = []
        # Create the header for the csv
        out.append(columns)
        for vid in vid_list:
            vid_dict = vid.to_dict()
            row = []
            for col in columns:
                val = vid_dict.get(col, "")
                row.append(val)
            out.append(row)
        return out

    def video_age_seconds(self, now_time: Optional[datetime] = None) -> float:
        """
        Returns the date published as a datetime object.
        """
        now_time = now_time or now_local()
        diff: timedelta = now_time - parse_datetime(self.date_published)
        return diff.total_seconds()


def parse_views(view_str: str) -> str:
    try:
        if view_str == "?":
            return view_str
        if view_str == "":
            return "0"
        multiplier = 1
        view_str = str(view_str).upper().replace(",", "")
        if "K" in view_str:
            view_str = view_str.replace("K", "")
            multiplier = 1000
        elif "M" in view_str:
            view_str = view_str.replace("M", "")
            multiplier = 1000 * 1000
    except BaseException as e:
        print(e)
    return str(int(float(view_str) * multiplier))


def test() -> None:
    url: str = "2021-03-29 01:13:15+00:00"
    d: Any = parse_datetime(url)
    print(f'"{d.isoformat()}"')


if __name__ == "__main__":
    test()
