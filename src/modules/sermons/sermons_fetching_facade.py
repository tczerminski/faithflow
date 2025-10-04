from datetime import datetime

from async_lru import alru_cache
from pydantic import BaseModel, HttpUrl

from src.modules.facade import FaithflowFacade


class SermonOverview(BaseModel):
    id: str
    title: str
    preacher: str
    thumbnail: bytes
    published_at: str


class SermonDetails(BaseModel):
    title: str
    preacher: str
    url: HttpUrl


class SermonsFetchingFacade(FaithflowFacade):
    def __init__(self, database):
        super().__init__()
        self.database = database

    @alru_cache(ttl=300)
    async def fetchone(self, sermon_id: str) -> SermonDetails | None:
        query = """
                SELECT TITLE, PREACHER, URL
                FROM SERMONS
                WHERE ID = ? \
                """
        async with self.database.execute(query, (sermon_id,)) as cursor:
            record = await cursor.fetchone()
            if record:
                title, preacher, url = record
                sermon = SermonDetails(
                    title=title,
                    preacher=preacher,
                    url=HttpUrl(url=url),
                )
                return sermon
        return None

    @alru_cache(ttl=300)
    async def preachers(self) -> list[str]:
        query = "SELECT DISTINCT PREACHER FROM SERMONS"
        preachers = []
        async with self.database.execute(query) as cursor:
            async for preacher, in cursor:
                preachers.append(preacher)
        preachers.sort()
        return preachers

    @alru_cache(ttl=300)
    async def fetchall(self) -> list[SermonOverview]:
        query = """
                SELECT ID, TITLE, PREACHER, URL, THUMBNAIL, PUBLISHED_AT
                FROM SERMONS
                """
        sermons = []
        async with self.database.execute(query) as cursor:
            async for sermon_id, title, preacher, url, thumbnail, published_at in cursor:
                published_at = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                sermon = SermonOverview(
                    id=sermon_id,
                    title=title,
                    preacher=preacher,
                    thumbnail=thumbnail,
                    published_at=published_at.strftime("%Y-%m-%d"),
                )
                sermons.append(sermon)
        sermons.sort(key=lambda s: datetime.fromisoformat(s.published_at), reverse=True)
        return sermons
