"""
    Flask app for the ytclip command line tool. Serves an index.html at port 80. Clipping
    api is located at /clip
"""
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import (
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
    Response,
)
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from vid_db.database import Database  # type: ignore
from vid_db.rss import to_rss

# from vid_db.database import Database
from vid_db.version import VERSION
from vid_db.video_info import VideoInfo

HERE = os.path.dirname(os.path.abspath(__file__))

executor = ThreadPoolExecutor(max_workers=8)
VID_DB = Database()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

STARTUP_DATETIME = datetime.now()


class RssResponse(Response):  # pylint: disable=too-few-public-methods
    """Returns an RSS response from a query."""

    media_type = "application/rss+xml"


class Query(BaseModel):  # pylint: disable=too-few-public-methods
    """Query structure."""

    start: datetime
    end: datetime
    channel_names: Optional[List[str]] = None
    limit: int = -1


class RssQuery(BaseModel):  # pylint: disable=too-few-public-methods
    """Query structure."""

    channel_name: str
    days: int = 7
    limit: int = -1


def log_error(msg: str) -> None:
    """Logs an error to the print stream."""
    print(msg)


# Mount all the static files.
app.mount("/www", StaticFiles(directory=os.path.join(HERE, "www")), "www")


# Redirect to index.html
@app.get("/")
async def index() -> RedirectResponse:
    """Returns index.html file"""
    return RedirectResponse(url="/docs", status_code=302)


# Redirect to favicon.ico
@app.get("/favicon.ico")
async def favicon() -> RedirectResponse:
    """Returns favico file."""
    return RedirectResponse(url="/www/favicon.ico")


@app.get("/version")
async def api_version() -> PlainTextResponse:
    """Api endpoint for getting the version."""
    return PlainTextResponse(VERSION)


@app.post("/query")
async def api_query(query: Query) -> JSONResponse:
    """Api endpoint for adding a video"""
    out: List[VideoInfo] = []
    if query.channel_names is None:
        query.channel_names = []
        out.extend(
            VID_DB.get_video_list(query.start, query.end, None, query.limit)
        )
    else:
        for channel_name in query.channel_names:
            data = VID_DB.get_video_list(
                query.start, query.end, channel_name, query.limit
            )
            out.extend(data)
    return JSONResponse(VideoInfo.to_plain_list(out))


@app.post("/rss/", response_model=List[VideoInfo])
async def api_rss_channel_feed(query: RssQuery) -> RssResponse:
    """Api endpoint for adding a video"""
    now = datetime.now()
    start = now - timedelta(days=query.days)
    kwargs = {}
    if query.limit > 0:
        kwargs["limit"] = query.limit
    out = VID_DB.get_video_list(start, now, query.channel_name, **kwargs)
    return RssResponse(to_rss(out))


@app.get("/rss/all", response_model=List[VideoInfo])
async def api_rss_all_feed(hours_ago: int) -> RssResponse:
    """Api endpoint for adding a video"""
    now = datetime.now()
    hours_ago = min(hours_ago, 48)
    start = now - timedelta(hours=hours_ago)
    out = VID_DB.get_video_list(start, now)
    return RssResponse(to_rss(out))


@app.put("/put/video")
async def api_add_video(video: VideoInfo) -> JSONResponse:
    """Api endpoint for adding a snapshot."""
    VID_DB.update(video)
    return JSONResponse({"ok": True})


@app.put("/put/videos")
async def api_add_videos(videos: List[VideoInfo]) -> JSONResponse:
    """Api endpoint for adding a snapshot."""
    VID_DB.update_many(videos)
    return JSONResponse({"ok": True})
