import asyncio
from abc import ABC


class FaithflowFacade(ABC):
    def __init__(self):
        self.daemons = []

    async def start(self): ...

    async def stop(self):
        for task in self.daemons:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
