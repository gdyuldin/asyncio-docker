from asyncio_docker.client import factory

from .env import (
    DOCKER_HOST,
    DOCKER_TLS_HOST,
    DOCKER_SOCKET,
    TLS_CA_CERT,
    TLS_CLIENT_CERT,
    TLS_CLIENT_KEY
)

def tcp_client():
    return factory(DOCKER_HOST)(DOCKER_HOST)

def tcp_tls_client():
    return factory(DOCKER_TLS_HOST)(
        DOCKER_TLS_HOST,
        tls=True,
        tls_verify=True,
        tls_ca_cert=TLS_CA_CERT,
        tls_cert=TLS_CLIENT_CERT,
        tls_key=TLS_CLIENT_KEY
    )

def unix_client():
    return factory(DOCKER_SOCKET)(DOCKER_SOCKET)
