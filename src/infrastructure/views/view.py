import base64
from datetime import timedelta

from starlette.templating import Jinja2Templates


class View:
    templates = Jinja2Templates(directory="templates")
    cache_ttl = timedelta(days=1)

    def __init__(self):
        def b64encode(data: bytes) -> str:
            return base64.b64encode(data).decode("utf-8")
        self.templates.env.filters["b64encode"] = b64encode

