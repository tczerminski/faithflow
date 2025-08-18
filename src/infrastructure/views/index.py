from fastapi import APIRouter
from starlette.responses import HTMLResponse, RedirectResponse

from src.infrastructure.views.view import View


class Index(View):
    @staticmethod
    def router():
        api = APIRouter()

        @api.get("/", response_class=HTMLResponse)
        async def index():
            return RedirectResponse(url="/sermons")

        return api
