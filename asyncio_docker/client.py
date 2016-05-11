from urllib.parse import urlsplit, urlunsplit, urljoin
import asyncio
import abc
import aiohttp


class BaseClient(object, metaclass=abc.ABCMeta):

    def __init__(self, host, *, headers=None, loop=None):
        self._host = host
        self._loop = loop or asyncio.get_event_loop()
        self._headers = headers or {}

    @property
    def host(self):
        return self._host

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

    def open(self):
        if hasattr(self, '_connector'):
            raise Exception("Client is in use.")
        self._connector = self.new_connector(loop=self._loop)
        self._sessions = {}

    def close(self):
        # Close all sessions
        for session in self._sessions.values():
            # Detach connector, we will close it last
            session.detach()
            session.close()
        # Close the connector
        self._connector.close()
        del self._connector
        del self._sessions

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()



class TCPClient(BaseClient):

    def __init__(self, host, *, tls=False, tls_verify=False,
            tls_cert=None, tls_key=None, tls_ca_cert=None,
            **kwargs):

        super(TCPClient, self).__init__(host, **kwargs)
        self._tls = tls
        self._tls_verify = tls_verify
        self._tls_cert = tls_cert
        self._tls_key = tls_key
        self._tls_ca_cert = tls_ca_cert

    def new_connector(self, loop):
        verify_ssl = self._tls_verify
        return aiohttp.TCPConnector(verify_ssl=verify_ssl, loop=loop)

    def resolve_url(self, url):
        o = urlsplit(self.host)
        n = o[:2] + (urljoin(o[2], url),) + o[3:]
        return urlunsplit(n)


class UnixClient(BaseClient):

    def new_connector(self, loop):
        o = urlsplit(self.host)
        return aiohttp.UnixConnector(path=o[2], loop=loop)

    def resolve_url(self, url):
        o = urlsplit('http://localhost')
        n = o[:2] + (urljoin(o[2], url),) + o[3:]
        return urlunsplit(n)


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
