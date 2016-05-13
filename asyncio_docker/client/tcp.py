import ssl
from urllib.parse import urlsplit, urlunsplit, urljoin
from aiohttp import TCPConnector

from .base import BaseClient


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

        return TCPConnector(loop=loop, **kwargs)

    def resolve_url(self, url):
        o = urlsplit(self.host)
        scheme = 'https' if self._tls else 'http'
        n = (scheme,) + o[1:2] + (urljoin(o[2], url),) + o[3:]
        return urlunsplit(n)
