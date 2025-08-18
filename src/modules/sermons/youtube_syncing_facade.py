import asyncio
from io import BytesIO

import aiohttp
import aiosqlite
import structlog
from PIL import Image
from pydantic import HttpUrl, SecretStr

from src.infrastructure.settings import YoutubeSettings, FaithflowSettings
from src.modules.facade import FaithflowFacade
from src.modules.sermons.sermon import Sermon


class YoutubeSyncingFacade(FaithflowFacade):
    def __init__(self, database, settings: YoutubeSettings):
        super().__init__()
        self.database = database
        self.url = settings.url
        self.channel_id = settings.channel_id
        self.api_key = settings.api_key
        self.logger = structlog.get_logger().bind(
            playlist_id=self.channel_id,
            yt_url=self.url.encoded_string(),
            logger=self.__class__.__name__,
        )

    async def sync(self):
        cursor = await self.database.execute(
            "SELECT ID FROM SERMONS"
        )
        ids = await cursor.fetchall()
        async for video in self.fetch_videos(ids):
            await self.database.execute(
                "INSERT OR IGNORE INTO SERMONS (ID, TITLE, PUBLISHED_AT, URL, PREACHER, THUMBNAIL) VALUES (?, ?, ?, ?, ?, ?)",
                (video.id, video.title, video.published_at, video.url.encoded_string(), video.preacher,
                 video.thumbnail),
            )
        await self.database.commit()

    async def downscale(self, thumbnail: bytes, size=(480, 360)):
        with Image.open(BytesIO(thumbnail)) as img:
            img.thumbnail(size)
            out = BytesIO()
            img.save(out, format="JPEG")
            return out.getvalue()

    async def fetch_best_thumbnail(self, video_id: str) -> bytes:
        urls = [
            f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
            f"https://i.ytimg.com/vi/{video_id}/sddefault.jpg",
            f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
        ]
        async with aiohttp.ClientSession() as session:
            for url in urls:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        thumbnail = await self.downscale(await resp.read())
                        return thumbnail
        raise ValueError("No thumbnail available")

    async def fetch_videos(self, skip: list[str]):
        page_token = None
        async with aiohttp.ClientSession() as session:
            while True:
                params = {
                    "key": self.api_key.get_secret_value(),
                    "part": "snippet",
                    "maxResults": 50,
                    "channelId": self.channel_id,
                    "order": "date",
                    "type": "video",
                }
                if page_token:
                    params["pageToken"] = page_token
                async with session.get(self.url.encoded_string(), params=params) as response:
                    response.raise_for_status()
                    payload = await response.json()
                    for item in payload.get("items", []):
                        snippet = item["snippet"]
                        if snippet["title"].startswith("Nabożeństwo"):
                            continue
                        video_id = item["id"]["videoId"]
                        if video_id in skip:
                            await self.logger.ainfo("sermon is already downloaded, skipping", video_id=video_id)
                            continue
                        video_url = f"https://youtube.com/watch?v={video_id}"
                        title = snippet["title"]
                        published_at = snippet["publishedAt"]
                        parts = title.rsplit(' - ', 1)
                        if len(parts) == 2:
                            preacher = parts[1].replace('br. ', '').strip()
                            title = parts[0].strip('" ')
                        thumbnail = await self.fetch_best_thumbnail(video_id)
                        yield Sermon(
                            id=video_id,
                            url=HttpUrl(url=video_url),
                            title=title,
                            published_at=published_at,
                            preacher=preacher,
                            thumbnail=thumbnail,
                        )
                    page_token = payload.get("nextPageToken")
                    if not page_token:
                        break
