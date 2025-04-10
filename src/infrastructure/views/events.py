from fastapi import APIRouter
from starlette.requests import Request

from src.infrastructure.views.view import View


class Events(View):

    def __init__(self, database):
        self.database = database

    def router(self):
        api = APIRouter()

        @api.get('/events')
        async def events(request: Request):
            response = self.templates.TemplateResponse(
                request=request,
                name="events.html.jinja",
                context={},
            )
            response.headers["Cache-Control"] = (
                f"public, max-age={self.cache_ttl.total_seconds()}"
            )
            return response

        return api