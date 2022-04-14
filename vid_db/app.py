"""
    Flask app for the ytclip command line tool. Serves an index.html at port 80. Clipping
    api is located at /clip
"""
import datetime
import os

# import ThreadPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import Dict

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from vid_db.version import VERSION

executor = ThreadPoolExecutor(max_workers=8)

HERE = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(HERE)
DATA = os.path.join(PROJECT_ROOT, "data")

os.makedirs(DATA, exist_ok=True)

app = FastAPI()


active_tokens: Dict[str, str] = {}
active_tokens_mutex = Lock()
STARTUP_DATETIME = datetime.datetime.now()


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
async def index(request: Request) -> RedirectResponse:
    """Returns index.html file"""
    params = {item[0]: item[1] for item in request.query_params.multi_items()}
    query = ""
    for key, value in params.items():
        if query == "":
            query += "?"
        query += f"{key}={value}&"
    return RedirectResponse(url=f"/www/index.html{query}", status_code=302)


# Redirect to favicon.ico
@app.get("/favicon.ico")
async def favicon() -> RedirectResponse:
    """Returns favico file."""
    return RedirectResponse(url="/www/favicon.ico")


@app.get("/version")
async def api_version() -> PlainTextResponse:
    """Api endpoint for getting the version."""
    return PlainTextResponse(VERSION)


@app.get("/query")
async def api_query(request: Request) -> PlainTextResponse:
    """Api endpoint for getting the version."""
    print(request)
    return PlainTextResponse(VERSION)
