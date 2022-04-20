"""
    Generates an rss stream from a list of VideoInfo object.
"""

from typing import Dict, List

from vid_db.date import iso_fmt
from vid_db.video_info import VideoInfo


def _rss_item(vid_info: VideoInfo) -> str:
    views = "0" if vid_info.views == "?" else vid_info.views
    return f"""
  <item>
    <title>{vid_info.title}</title>
    <published>{iso_fmt(vid_info.date_published)}</published>
    <lastupdated>{iso_fmt(vid_info.date_lastupdated)}</lastupdated>
    <url>{vid_info.url}</url>
    <channel_url>{vid_info.channel_url}</channel_url>
    <channel_name>{vid_info.channel_name}</channel_name>
    <description>{vid_info.description}</description>
    <image>{vid_info.img_src}</image>
    <duration>{vid_info.duration}</duration>
    <views>{views}</views>
    <host>{vid_info.source}</host>
    <iframe>{vid_info.iframe_src}</iframe>
  </item>
"""


def to_rss(data: List[VideoInfo]) -> str:
    """
    Returns a list of RSS items as a string.
    """
    out = """
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
"""
    channel_videos: Dict[str, List[VideoInfo]] = {}
    for vid_info in data:
        channel_videos.setdefault(vid_info.channel_name, []).append(vid_info)
    for channel_name, videos in channel_videos.items():
        out += f"  <channel><title>{channel_name}</title>"
        for vid_info in videos:
            out += _rss_item(vid_info)
        out += "  </channel>"
    return out
