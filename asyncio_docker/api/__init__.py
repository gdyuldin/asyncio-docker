# Register
from . import (
    container,
    image,
    network,
    volume,
    event,
    exec,
    node,
    service,
    task
)

from asyncio_docker.registry import Registry as RemoteAPI

__all__ = [
    'RemoteAPI'
]
