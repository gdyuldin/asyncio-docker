from urllib.parse import urlsplit, urlunsplit, urljoin

import asyncio
import abc
import aiohttp


class BaseClient(object, metaclass=abc.ABCMeta):

    def __init__(self, host, *, loop=None):
        self.host = host
        self.loop = loop or asyncio.get_event_loop()
        self.connector = self.new_connector()

    @abc.abstractmethod
    def new_connector(self):
        pass

    @abc.abstractmethod
    def resolve_url(self, url):
        pass

    def _client_kwargs(self, **kwargs):
        return dict(connector=self.connector, loop=self.loop, **kwargs)

    def request(self, method, url, **kwargs):
        return aiohttp.request(method, self.resolve_url(url), **self._client_kwargs(**kwargs))

    def ws_connect(self, url, **kwargs):
        return aiohttp.ws_connect(self.resolve_url(url), **self._client_kwargs(**kwargs))

    def get(self, url, **kwargs):
        return self.request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        return self.request('POST', url, **kwargs)

    def put(self, url, **kwargs):
        return self.request('PUT', url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request('DELETE', url, **kwargs)


class TCPClient(BaseClient):

    def new_connector(self):
        return aiohttp.TCPConnector(loop=self.loop)

    def resolve_url(self, url):
        o = urlsplit(self.host)
        n = o[:2] + tuple([urljoin(o[2], url)]) + o[3:]
        return urlunsplit(n)


class UnixClient(BaseClient):
    pass


_clients = {
    'tcp': TCPClient,
    'unix': UnixClient
}

def factory(host):
    o = urlsplit(host)
    if o.scheme in _clients:
        return _clients[o.scheme]
    else:
        raise ValueError(o.scheme)
