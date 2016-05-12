from asyncio_docker.client import factory

from .env import (
    DOCKER_HOST,
    DOCKER_TLS_HOST,
    DOCKER_SOCKET,
    TLS_CA_CERT,
    TLS_CLIENT_CERT,
    TLS_CLIENT_KEY
)

TCP_CLIENT = factory(DOCKER_HOST)(DOCKER_HOST)

TCP_TLS_CLIENT = factory(DOCKER_TLS_HOST)(
    DOCKER_TLS_HOST,
    tls=True,
    tls_verify=True,
    tls_ca_cert=TLS_CA_CERT,
    tls_cert=TLS_CLIENT_CERT,
    tls_key=TLS_CLIENT_KEY
)

UNIX_CLIENT = factory(DOCKER_SOCKET)(DOCKER_SOCKET)

CLIENTS = [
    TCP_CLIENT,
    TCP_TLS_CLIENT,
    UNIX_CLIENT
]
