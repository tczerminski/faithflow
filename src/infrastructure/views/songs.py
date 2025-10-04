import structlog
from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import HTMLResponse

from src.infrastructure.views.view import View
from src.modules.songs.songs_fetching_facade import SongsFetchingFacade


class Songs(View):
    def __init__(self, facade: SongsFetchingFacade):
        super().__init__()
        self.facade = facade
        self.logger = structlog.get_logger().bind(
            logger=Songs.__class__.__name__,
        )

    def router(self):
        api = APIRouter()

        @api.get("/songs", response_class=HTMLResponse)
        async def songs(request: Request):
            model = await self.facade.fetchall()
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
            fetched = await self.facade.fetchone(song_id)
            response = self.templates.TemplateResponse(
                request=request,
                name="song.html.jinja",
                context={"song": fetched},
            )
            response.headers["Cache-Control"] = (
                f"public, max-age={self.cache_ttl.total_seconds()}"
            )
            return response

        return api
