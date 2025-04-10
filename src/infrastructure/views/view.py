from datetime import timedelta

from starlette.templating import Jinja2Templates


class View:
    templates = Jinja2Templates(directory="templates")
    cache_ttl = timedelta(days=1)
