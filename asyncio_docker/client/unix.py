from urllib.parse import urlsplit, urlunsplit, urljoin
from aiohttp import UnixConnector

from .base import BaseClient


class UnixClient(BaseClient):

    HOST = 'http://localhost'

    def __init__(self, host, **kwargs):
        super(UnixClient, self).__init__(self.HOST, **kwargs)
        self._path = urlsplit(host)[2]

    def new_connector(self, loop):
        return UnixConnector(path=self._path, loop=loop)

    def resolve_url(self, url):
        o = urlsplit(self.host)
        n = o[:2] + (urljoin(o[2], url),) + o[3:]
        return urlunsplit(n)
