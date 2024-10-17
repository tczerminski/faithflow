import os
from contextlib import asynccontextmanager

import sentry_sdk
import structlog.stdlib
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.gzip import GZipMiddleware

from fastapi import FastAPI, Request

from load_songs import load_songs

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

songs = {}


@asynccontextmanager
async def lifespan(_):
    global songs
    songs = load_songs()
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
# noinspection PyTypeChecker
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)

templates = Jinja2Templates(directory="templates")

logger = structlog.stdlib.get_logger()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, page: int = 1, per_page: int = 10):
    await logger.ainfo("getting songs", count=len(songs.items()))
    model = list(songs.values())

    def sorter(song):
        return song["id"]

    model.sort(key=sorter)
    total_pages = len(model) // per_page
    model = model[(page - 1) * per_page: page * per_page]
    return templates.TemplateResponse(
        request=request,
        name="songs.html.jinja",
        context={
            "songs": model,
            "page": page,
            "total_pages": total_pages,
        },
    )


@app.get("/songs/{song_id}", response_class=HTMLResponse)
async def get_song(request: Request, song_id: int):
    song = songs.get(song_id, {})
    await logger.ainfo("getting song", song_id=song_id)
    return templates.TemplateResponse(
        request=request,
        name="song.html.jinja",
        context={
            "song": song,
        },
    )
