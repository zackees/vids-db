"""
    Flask app for the ytclip command line tool. Serves an index.html at port 80. Clipping
    api is located at /clip
"""
import os

# import ThreadPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import List, Optional

# import pytz
from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from vid_db.database import Database  # type: ignore

# from vid_db.database import Database
from vid_db.version import VERSION
from vid_db.video_info import VideoInfo

executor = ThreadPoolExecutor(max_workers=8)

HERE = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(HERE)
DATA = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA, exist_ok=True)
DEFAULT_VID_DB_FILE = os.path.join(DATA, "vid_db.sqlite")
VID_DB_FILE = os.environ.get("VID_DB_FILE", DEFAULT_VID_DB_FILE)

VID_DB = Database(VID_DB_FILE)

app = FastAPI()

STARTUP_DATETIME = datetime.now()


class Query(BaseModel):  # pylint: disable=too-few-public-methods
    """Query structure."""

    start: datetime
    end: datetime
    channel_names: Optional[List[str]] = None
    limit: int = -1


def get_file(filename):  # pragma: no cover
    """Get the contents of a file."""
    try:
        src = os.path.join(HERE, filename)
        # Specify binary mode to avoid decoding errors
        return open(src, mode="rb").read()  # pytype: disable=unspecified-encoding
    except IOError as exc:
        return str(exc)


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
    # print(query)
    out: List[VideoInfo] = []
    if query.channel_names is None:
        query.channel_names = []
        out.extend(VID_DB.get_video_list(query.start, query.end, None, query.limit))
    else:
        for channel_name in query.channel_names:
            data = VID_DB.get_video_list(query.start, query.end, channel_name, query.limit)
            out.extend(data)
    # vid_db().update_many(query.vids)
    return JSONResponse(VideoInfo.to_plain_list(out))


@app.get("/feed/days/{number_of_hours}")
async def api_feed_days(number_of_hours: int) -> JSONResponse:
    """Api endpoint for adding a video"""
    # print(query)
    now = datetime.now()
    start = now - timedelta(hours=number_of_hours)
    out = VID_DB.get_video_list(start, now)
    return JSONResponse(VideoInfo.to_plain_list(out))


@app.put("/update/video")
async def api_add_video(video: VideoInfo) -> JSONResponse:
    """Api endpoint for adding a snapshot."""
    VID_DB.update(video)
    return JSONResponse({"ok": True})


@app.put("/update/videos")
async def api_add_videos(videos: List[VideoInfo]) -> JSONResponse:
    """Api endpoint for adding a snapshot."""
    VID_DB.update_many(videos)
    return JSONResponse({"ok": True})
