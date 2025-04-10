from fastapi import APIRouter, Query
from starlette.requests import Request
from src.infrastructure.views.view import View


class Sermons(View):
    def __init__(self, database):
        self.database = database

    def router(self):
        api = APIRouter()

        @api.get("/sermons")
        async def sermons(
            request: Request,
            page: int = Query(1, ge=1),
            page_size: int = Query(10, ge=1, le=100),
        ):
            offset = (page - 1) * page_size
            limit = page_size + 1
            rows = []
            async with self.database.execute(
                """
                SELECT * FROM SERMONS
                ORDER BY CREATED_AT DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            ) as cursor:
                async for row in cursor:
                    rows.append(row)
            await cursor.close()
            has_next = len(rows) > page_size
            if has_next:
                rows = rows[:-1]
            items = [dict(row) for row in rows]
            response = self.templates.TemplateResponse(
                request=request,
                name="sermons.html.jinja",
                context={
                    "videos": items,
                    "page": page,
                    "page_size": page_size,
                    "has_next": has_next,
                    "next_page": page + 1 if has_next else None,
                    "prev_page": page - 1 if page > 1 else None,
                },
            )
            response.headers["Cache-Control"] = (
                f"public, max-age={self.cache_ttl.total_seconds()}"
            )
            return response

        return api
