from urllib.parse import urlsplit, urlunsplit, urljoin
import ssl
import asyncio
import abc
import aiohttp


class BaseClient(object, metaclass=abc.ABCMeta):

    def __init__(self, host, *, headers=None, loop=None, **kwargs):
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

    def __init__(self, host, *, tls=False, tls_verify=True,
            tls_cert=None, tls_key=None, tls_ca_cert=None,
            **kwargs):

        super(TCPClient, self).__init__(host, **kwargs)
        self._tls = tls
        self._tls_verify = tls_verify
        self._tls_cert = tls_cert
        self._tls_key = tls_key
        self._tls_ca_cert = tls_ca_cert

    def new_connector(self, loop):
        kwargs = {}
        if self._tls:
            ssl_context = ssl.create_default_context(
                purpose=ssl.Purpose.SERVER_AUTH
            )

            if self._tls_ca_cert:
                ssl_context.load_verify_locations(cafile=self._tls_ca_cert)

            if not self._tls_verify:
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

            if self._tls_cert:
                ssl_context.load_cert_chain(self._tls_cert, self._tls_key)

            kwargs.update({
                'ssl_context': ssl_context
            })

        return aiohttp.TCPConnector(loop=loop, **kwargs)

    def resolve_url(self, url):
        o = urlsplit(self.host)
        scheme = 'https' if self._tls else 'http'
        n = (scheme,) + o[1:2] + (urljoin(o[2], url),) + o[3:]
        return urlunsplit(n)


class UnixClient(BaseClient):

    HOST = 'http://localhost'

    def __init__(self, host, **kwargs):
        super(UnixClient, self).__init__(self.HOST, **kwargs)
        self._path = urlsplit(host)[2]

    def new_connector(self, loop):
        return aiohttp.UnixConnector(path=self._path, loop=loop)

    def resolve_url(self, url):
        o = urlsplit(self.host)
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
