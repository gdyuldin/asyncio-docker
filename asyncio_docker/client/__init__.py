from urllib.parse import urlsplit

from .tcp import TCPClient
from .unix import UnixClient
from .errors import ClientError, ClientClosedError


_schemes = {
    'tcp': TCPClient,
    'unix': UnixClient
}


def client_factory(host):
    o = urlsplit(host)
    if o.scheme in _schemes:
        return _schemes[o.scheme]
    else:
        raise ValueError(o.scheme)


__all__ = [
    'TCPClient',
    'UnixClient',
    'client_factory'
]
