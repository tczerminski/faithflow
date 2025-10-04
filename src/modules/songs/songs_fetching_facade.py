import orjson
from async_lru import alru_cache
from pydantic import BaseModel

from src.modules.facade import FaithflowFacade


class Verse(BaseModel):
    lines: list[str]


class Song(BaseModel):
    id: int
    title: str
    verses: list[Verse]


class SongsFetchingFacade(FaithflowFacade):
    def __init__(self, database):
        super().__init__()
        self.database = database

    @alru_cache(ttl=300)
    async def fetchone(self, song_id: int) -> Song | None:
        query = """
                SELECT ID, TITLE, VERSES
                FROM SONGS
                WHERE ID = ? \
                """
        async with self.database.execute(query, (song_id,)) as cursor:
            record = await cursor.fetchone()
            if record:
                song_id, title, verses = record
                song = Song(
                    id=song_id,
                    title=title,
                    verses=[],
                )
                for verse in orjson.loads(verses):
                    song.verses.append(
                        Verse(
                            lines=verse["lines"],
                        )
                    )
                return song
            return None

    @alru_cache(ttl=300)
    async def fetchall(self) -> list[Song]:
        query = """
                SELECT ID, TITLE, VERSES
                FROM SONGS \
                """
        songs = []
        async with self.database.execute(query) as cursor:
            async for song_id, title, verses in cursor:
                song = Song(
                    id=song_id,
                    title=title,
                    verses=[],
                )
                for verse in orjson.loads(verses):
                    song.verses.append(
                        Verse(
                            lines=verse["lines"],
                        )
                    )
                songs.append(song)
        return songs
