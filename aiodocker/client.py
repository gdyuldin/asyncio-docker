from urllib.parse import urlsplit, urlunsplit, urljoin

import abc
import aiohttp


class BaseClient(object, metaclass=abc.ABCMeta):

    def __init__(self, host, *, loop=None):
        self._connector = self.new_connector(host, loop)
        self._host = host

    @abc.abstractmethod
    def new_connector(self, host, loop=None):
        pass

    @abc.abstractmethod
    def resolve_url(self, url):
        pass

    def request(self, method, url, **kwargs):
        return aiohttp.request(method, self.resolve_url(url), **kwargs)

    def get(self, url, **kwargs):
        return aiohttp.get(self.resolve_url(url), **kwargs)

    def post(self, url, **kwargs):
        return aiohttp.post(self.resolve_url(url), **kwargs)

    def put(self, url, **kwargs):
        return aiohttp.put(self.resolve_url(url), **kwargs)

    def delete(self, url, **kwargs):
        return aiohttp.delete(self.resolve_url(url), **kwargs)

    def ws_connect(self, url, **kwargs):
        return aiohttp.ws_connect(self.resolve_url(url), **kwargs)


class TCPClient(BaseClient):

    def new_connector(self, host, loop=None):
        return aiohttp.TCPConnector(loop=loop)

    def resolve_url(self, url):
        o = urlsplit(self._host)
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
