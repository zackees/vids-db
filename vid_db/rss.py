"""
    Generates an rss stream from a list of VideoInfo object.
"""

from typing import Dict, List

from vid_db.date import iso_fmt
from vid_db.video_info import VideoInfo


def to_rss(data: List[VideoInfo]) -> str:
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
