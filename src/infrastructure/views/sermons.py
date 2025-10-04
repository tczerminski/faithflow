from fastapi import APIRouter, Query
from starlette.requests import Request
from src.infrastructure.views.view import View
from src.modules.sermons.sermons_fetching_facade import SermonsFetchingFacade


class Sermons(View):
    def __init__(self, facade: SermonsFetchingFacade):
        super().__init__()
        self.facade = facade

    def router(self):
        api = APIRouter()

        @api.get("/sermons")
        async def sermons(request: Request):
            response = self.templates.TemplateResponse(
                request=request,
                name="sermons.html.jinja",
                context={
                    "sermons": await self.facade.fetchall(),
                },
            )
            response.headers["Cache-Control"] = (
                f"public, max-age={self.cache_ttl.total_seconds()}"
            )
            return response

        @api.get("/sermons/{sermon_id}")
        async def sermon(request: Request, sermon_id: str):
            response = self.templates.TemplateResponse(
                request=request,
                name="sermon.html.jinja",
                context={
                    "sermon": await self.facade.fetchone(sermon_id),
                },
            )
            response.headers["Cache-Control"] = (
                f"public, max-age={self.cache_ttl.total_seconds()}"
            )
            return response

        return api
