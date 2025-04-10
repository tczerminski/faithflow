import structlog
from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import HTMLResponse

from src.infrastructure.views.view import View


class Songs(View):
    def __init__(self, database):
        self.database = database
        self.logger = structlog.get_logger().bind(
            logger=Songs.__class__.__name__,
        )

    def router(self):
        api = APIRouter()

        @api.get("/songs", response_class=HTMLResponse)
        async def songs(request: Request):
            await self.logger.ainfo("getting songs", count=len(songs.items()))
            model = list(songs.values())
            model.sort(key=lambda x: x["id"])
            response = self.templates.TemplateResponse(
                request=request,
                name="songs.html.jinja",
                context={"songs": model},
            )
            response.headers["Cache-Control"] = (
                f"public, max-age={self.cache_ttl.total_seconds()}"
            )
            return response

        @api.get("/songs/{song_id}", response_class=HTMLResponse)
        async def song(request: Request, song_id: int):
            persisted = songs.get(song_id, {})
            await self.logger.ainfo("getting song", song_id=song_id)
            response = self.templates.TemplateResponse(
                request=request,
                name="song.html.jinja",
                context={"song": persisted},
            )
            response.headers["Cache-Control"] = (
                f"public, max-age={self.cache_ttl.total_seconds()}"
            )
            return response

        return api
