from urllib.parse import urlsplit, urlunsplit, urljoin
import asyncio
import abc
import aiohttp


class BaseClient(object, metaclass=abc.ABCMeta):

    def __init__(self, host, *, headers=None, loop=None):
        self.host = host
        self._loop = loop or asyncio.get_event_loop()
        self._connector = None
        self._headers = dict(headers or {})

    def set_headers(self, **headers):
        self._headers = headers

    @abc.abstractmethod
    def new_connector(self, loop):
        pass

    @abc.abstractmethod
    def resolve_url(self, url):
        pass

    def close(self):
        if self._connector is not None and not self._connector.closed:
            self._loop.run_until_complete(self._connector.close())
            self._connector = None

    def _get_connector(self):
        if self._connector is None or self._connector.closed:
            self._connector = self.new_connector(self._loop)
        return self._connector

    def _client_kwargs(self, **kwargs):
        headers = self._headers
        if 'headers' in kwargs:
            headers = dict(headers, **kwargs.pop('headers'))

        return dict(
            connector=self._get_connector(),
            loop=self._loop,
            headers=headers,
            **kwargs
        )

    def request(self, method, url, **kwargs):
        return aiohttp.request(
            method,
            self.resolve_url(url),
            **self._client_kwargs(**kwargs)
        )

    def ws_connect(self, url, **kwargs):
        return aiohttp.ws_connect(
            self.resolve_url(url),
            **self._client_kwargs(**kwargs)
        )

    def get(self, url, **kwargs):
        return self.request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        return self.request('POST', url, **kwargs)

    def put(self, url, **kwargs):
        return self.request('PUT', url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request('DELETE', url, **kwargs)


class TCPClient(BaseClient):

    def new_connector(self, loop):
        return aiohttp.TCPConnector(loop=loop)

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
