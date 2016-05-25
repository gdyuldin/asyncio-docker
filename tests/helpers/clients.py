from asyncio_docker.client import client_factory
import os

from .env import (
    DOCKER_HOST,
    DOCKER_TLS_HOST,
    DOCKER_SOCKET,
    SSL_DIR,
    TLS_CA_CERT,
    TLS_CLIENT_CERT,
    TLS_CLIENT_KEY
)

def tcp_client(host=DOCKER_HOST):
    return client_factory(host)(host)

def tcp_tls_client(host=DOCKER_TLS_HOST):
    return client_factory(host)(
        host,
        tls=True,
        tls_verify=True,
        tls_ca_cert=os.path.join(SSL_DIR, TLS_CA_CERT),
        tls_cert=os.path.join(SSL_DIR, TLS_CLIENT_CERT),
        tls_key=os.path.join(SSL_DIR, TLS_CLIENT_KEY)
    )

def unix_client(host=DOCKER_SOCKET):
    return client_factory(host)(host)
