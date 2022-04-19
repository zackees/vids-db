# disable pylint for the entire file
# pylint: disable=all

from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel

from vid_db.date import iso_fmt, now_local, parse_datetime


class VideoInfo(BaseModel):
    """In memory reporesentation of a video article."""

    channel_name: str
    title: str
    date_published: datetime  # from the scraped website
    date_discovered: datetime  # generated during scrape
    date_lastupdated: datetime
    channel_url: str
    source: str
    url: str
    duration: str  # units = seconds.
    description: str
    img_src: str
    iframe_src: str
    views: int
    # rank: Optional[float] = None  # optional stdev rank.

    def to_dict(self) -> Dict:
        """Generates a dictionary representing this class instance."""
        out = {
            "channel_name": self.channel_name,
            "title": self.title,
            "date_published": iso_fmt(self.date_published),
            "date_discovered": iso_fmt(self.date_discovered),
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
    def from_json_str(cls, data: str) -> VideoInfo:
        """Deserializes from dictionary json str back to VideoInfo"""
        d = json.loads(data)
        return VideoInfo.from_dict(d)

    @classmethod
    def from_dict(cls, data: Dict) -> VideoInfo:
        """Deserializes from dictionary back to VideoInfo"""
        views = _parse_views(data["views"])

        return VideoInfo(
            channel_name=data["channel_name"],
            title=data["title"],
            date_published=parse_datetime(data["date_published"]),
            date_discovered=parse_datetime(data["date_discovered"]),
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
    def from_list_of_dicts(cls, data: List[Dict]) -> List[VideoInfo]:
        out: List[VideoInfo] = []
        for datum in data:
            vid = VideoInfo.from_dict(datum)
            out.append(vid)
        return out

    @classmethod
    def to_plain_list(cls, data: List[VideoInfo]) -> List[Dict]:
        out = []
        vid_info: VideoInfo
        for vid_info in data:
            d = vid_info.to_dict()
            out.append(d)
        return out

    @classmethod
    def to_rss(cls, data: List[VideoInfo]) -> str:
        """
        Returns a list of RSS items as a string.
        """
        out = """
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:cc="http://web.resource.org/cc/" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:media="http://search.yahoo.com/mrss/" xmlns:content="http://purl.org/rss/1.0/modules/content/"  xmlns:podcast="https://podcastindex.org/namespace/1.0"  xmlns:googleplay="http://www.google.com/schemas/play-podcasts/1.0" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
</rss>
"""
        channel_videos: Dict[str, List[VideoInfo]] = {}
        for vid_info in data:
            channel_videos.setdefault(vid_info.channel_name, []).append(vid_info)
        for channel_name, videos in channel_videos.items():
            out += f"<channel><title>{channel_name}</title>"
            for vid_info in videos:
                out += f"""
<item>
<title>[!CDATA[{vid_info.title}]]</title>
<link>{vid_info.url}</link>
<description>[!CDATA[{vid_info.description}]]</description>
<pubDate>{iso_fmt(vid_info.date_published)}</pubDate>
<guid>{vid_info.url}</guid>
</item>
"""
            out += "</channel>"
        return out

    @classmethod
    def to_compact_csv(
        cls, vid_list: List[VideoInfo], exclude_columns: Optional[Set[str]] = None
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


def _parse_views(view_str: str) -> str:
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
