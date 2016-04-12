from urllib.parse import urlsplit, urlunsplit, urljoin
import asyncio
import abc
import aiohttp


class BaseClient(object, metaclass=abc.ABCMeta):

    def __init__(self, host, *, headers=None, loop=None):
        self.host = host
        self._loop = loop or asyncio.get_event_loop()
        self._headers = headers or {}

    def set_headers(self, **headers):
        self._headers = headers

    @abc.abstractmethod
    def new_connector(self, loop):
        pass

    @abc.abstractmethod
    def resolve_url(self, url):
        pass

    def resolve_kwargs(self, **kwargs):
        headers = self._headers
        if 'headers' in kwargs:
            headers = dict(headers, **kwargs.pop('headers'))

        return dict(
            headers=headers,
            **kwargs
        )

    def _get_session(self, response_class=aiohttp.ClientResponse):
        if response_class not in self._sessions:
            self._sessions[response_class] = aiohttp.ClientSession(
                connector=self._connector,
                response_class=response_class,
                loop=self._loop
            )

        return self._sessions[response_class]

    def request(self, method, url, response_class=aiohttp.ClientResponse, **kwargs):
        return self._get_session(response_class=response_class).request(
            method,
            self.resolve_url(url),
            **self.resolve_kwargs(**kwargs)
        )

    def get(self, url, **kwargs):
        return self.request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        return self.request('POST', url, **kwargs)

    def put(self, url, **kwargs):
        return self.request('PUT', url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request('DELETE', url, **kwargs)

    def __enter__(self):
        if hasattr(self, '_connector'):
            raise Exception("Client is in use.")
        self._connector = self.new_connector(loop=self._loop)
        self._sessions = {}
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Close all sessions
        for session in self._sessions.values():
            # Detach connector, we will close it last
            session.detach()
            session.close()
        # Close the connector
        self._connector.close()
        del self._connector
        del self._sessions



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
