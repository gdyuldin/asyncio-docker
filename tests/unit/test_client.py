import unittest

from helpers import aio
from helpers.docker import (
    TCP_DAEMON,
    TCP_TLS_DAEMON,
    UNIX_DAEMON
)
from helpers.env import (
    DOCKER_HOST,
    DOCKER_TLS_HOST,
    DOCKER_SOCKET,
    TLS_CA_CERT,
    TLS_CLIENT_CERT,
    TLS_CLIENT_KEY
)

from asyncio_docker.client import factory


class ClientTestCase(unittest.TestCase):

    @aio.run_until_complete()
    async def test_tcp_client(self):
        async with TCP_DAEMON as context:
            client = factory(DOCKER_HOST)(DOCKER_HOST)
            with client as session:
                async with session.get('/') as res:
                    assert res.status == 404

    @aio.run_until_complete()
    async def test_tls_client(self):
        async with TCP_TLS_DAEMON as context:
            client = factory(DOCKER_TLS_HOST)(DOCKER_TLS_HOST, tls=True, tls_verify=True, tls_ca_cert=TLS_CA_CERT, tls_cert=TLS_CLIENT_CERT, tls_key=TLS_CLIENT_KEY)
            with client as session:
                async with session.get('/') as res:
                    assert res.status == 404

    @aio.run_until_complete()
    async def test_unix_client(self):
        async with UNIX_DAEMON as context:
            client = factory(DOCKER_SOCKET)(DOCKER_SOCKET)
            with client as session:
                async with session.get('/') as res:
                    assert res.status == 404
