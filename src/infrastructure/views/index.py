from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

from src.infrastructure.views.view import View


class Index(View):
    @staticmethod
    def router():
        api = APIRouter()

        @api.get("/", response_class=HTMLResponse)
        async def index():
            return RedirectResponse(url="/events")

        return api
