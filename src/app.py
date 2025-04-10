import os
from contextlib import asynccontextmanager

import aiosqlite
import sentry_sdk
from fastapi import FastAPI
from starlette.middleware.gzip import GZipMiddleware
from starlette.staticfiles import StaticFiles

from src.infrastructure.settings import FaithflowSettings
from src.infrastructure.views.events import Events
from src.infrastructure.views.index import Index
from src.infrastructure.views.sermons import Sermons
from src.infrastructure.views.songs import Songs
from src.modules.sermons.youtube_syncing_facade import YoutubeSyncingFacade
from src.modules.songs.songs_fetching_facade import SongsFetchingFacade

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)


@asynccontextmanager
async def lifespan(faithflow: FastAPI):
    # noinspection PyArgumentList
    settings = FaithflowSettings()
    async with aiosqlite.connect(database="./faithflow.data") as database:
        views = [
            Index(),
            Sermons(database),
            Songs(database),
            Events(database),
        ]
        for view in views:
            faithflow.include_router(view.router())
        facades = [
            YoutubeSyncingFacade(database, settings.youtube),
            SongsFetchingFacade(database),
        ]
        for facade in facades:
            await facade.start()
        yield
        for facade in facades:
            await facade.stop()


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
# noinspection PyTypeChecker
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)
