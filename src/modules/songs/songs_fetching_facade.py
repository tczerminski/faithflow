from src.modules.facade import FaithflowFacade


class SongsFetchingFacade(FaithflowFacade):
    def __init__(self, database):
        super().__init__()
        self.database = database

    async def fetch(self): ...
