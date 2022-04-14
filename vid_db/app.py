"""
    Flask app for the ytclip command line tool. Serves an index.html at port 80. Clipping
    api is located at /clip
"""
import os

# import ThreadPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
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
VID_DB_FILE = os.path.join(DATA, "vid_db.sqlite")

VID_DB = None


def vid_db() -> Database:
    """Returns the video database."""
    global VID_DB  # pylint: disable=global-statement
    if VID_DB is None:
        VID_DB = Database(VID_DB_FILE)
    return VID_DB


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
        out.extend(vid_db().get_video_list(query.start, query.end, None, query.limit))
    else:
        for channel_name in query.channel_names:
            data = vid_db().get_video_list(
                query.start, query.end, channel_name, query.limit
            )
            out.extend(data)
    # vid_db().update_many(query.vids)
    return JSONResponse(VideoInfo.to_plain_list(out))


@app.put("/update/video")
async def api_add_video(video: VideoInfo) -> JSONResponse:
    """Api endpoint for adding a snapshot."""
    vid_db().update(video)
    return JSONResponse({"ok": True})


@app.put("/update/videos")
async def api_add_videos(videos: List[VideoInfo]) -> JSONResponse:
    """Api endpoint for adding a snapshot."""
    vid_db().update_many(videos)
    return JSONResponse({"ok": True})
