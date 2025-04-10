from datetime import timedelta, datetime

import aiohttp
from pydantic import BaseModel, Field, HttpUrl

from src.infrastructure.daemon import daemon
from src.infrastructure.settings import YoutubeSettings
from src.modules.facade import FaithflowFacade


class YoutubeSermon(BaseModel):
    id: str = Field(serialization_alias="_id")
    title: str
    published_at: datetime
    url: HttpUrl


class YoutubeSyncingFacade(FaithflowFacade):
    def __init__(self, database, settings: YoutubeSettings):
        super().__init__()
        self.database = database
        self.url = settings.url
        self.channel_id = settings.channel_id
        self.api_key = settings.api_key

    async def start(self):
        self.daemons = [
            daemon(interval=timedelta(hours=1), func=self.sync),
        ]

    async def sync(self):
        page_token = None
        async with aiohttp.ClientSession() as session:
            while True:
                params = {
                    "channelId": self.channel_id,
                    "part": "id",
                    "key": self.api_key.get_secret_value(),
                    "type": "video",
                    "maxResults": 50,
                    "order": "date",
                }
                if page_token:
                    params["pageToken"] = page_token
                async with session.get(f"{self.url}/search", params=params) as response:
                    response.raise_for_status()
                    payload = response.json()
                page_token = payload.get("nextPageToken")
                for video in payload["items"]:
                    if not video["snippet"]["liveBroadcastContent"] == "none":
                        continue
                    params = {
                        "part": "snippet",
                        "id": video["id"]["videoId"],
                        "key": self.api_key.get_secret_value(),
                    }
                    async with session.get(
                        f"{self.url}/videos", params=params
                    ) as response:
                        response.raise_for_status()
                        payload = response.json()
                        await self.database.save(payload)
                if not page_token:
                    break
