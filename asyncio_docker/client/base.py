from urllib.parse import urlsplit, urlunsplit, urljoin
import asyncio
import abc
import aiohttp

from asyncio_docker import API_VERSION
from .errors import ClientError, ClientClosedError


class BaseClient(object, metaclass=abc.ABCMeta):

    def __init__(self, host, *, headers=None, version=API_VERSION, loop=None):
        self._host = host
        self._headers = headers or {}
        self._version = version
        self._loop = loop or asyncio.get_event_loop()

    @property
    def host(self):
        return self._host

    def _get_headers(self):
        return dict(self._headers)

    def _set_headers(self, headers):
        self._headers = headers or {}

    headers = property(_get_headers, _set_headers)

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

    def _resolve_url(self, url):
        url = self.resolve_url(url)
        if self._version is not None:
            o = urlsplit(url)
            n = o[:2] + (urljoin('v%s.%s' % self._version, o[2]),) + o[3:]
            url = urlunsplit(n)
        return url


    def _get_session(self, response_class=aiohttp.ClientResponse):
        if self.is_closed():
            raise ClientClosedError("Cannot get a session, client is closed")

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
            self._resolve_url(url),
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

    def open(self):
        if not self.is_closed():
            raise ClientError("Client needs to be closed before it can be opened")

        self._connector = self.new_connector(loop=self._loop)
        self._sessions = {}
        return self

    def is_closed(self):
        return not hasattr(self, '_connector')

    def close(self):
        if self.is_closed():
            raise ClientError("Client is already closed")

        for session in self._sessions.values():
            # Detach connector before closing session.
            session.detach()
            session.close()

        self._connector.close()

        del self._connector
        del self._sessions

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
