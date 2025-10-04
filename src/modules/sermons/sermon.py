from pydantic import BaseModel, HttpUrl


class Sermon(BaseModel):
    id: str
    title: str
    published_at: str
    preacher: str
    url: HttpUrl
    thumbnail: bytes
