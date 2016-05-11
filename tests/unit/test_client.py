import unittest

from helpers import aio
from helpers.docker import DockerDaemonContext
from helpers.env import DOCKER_HOST, DOCKER_SOCKET

from asyncio_docker.client import factory


TCP_DAEMON = DockerDaemonContext(DOCKER_HOST)
UNIX_DAEMON = DockerDaemonContext(DOCKER_SOCKET)


class ClientTestCase(unittest.TestCase):

    @aio.run_until_complete()
    async def test_tcp_client(self):
        async with TCP_DAEMON as context:
            client = factory(DOCKER_HOST)(DOCKER_HOST)
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
