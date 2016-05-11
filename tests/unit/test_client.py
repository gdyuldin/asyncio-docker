import unittest

from helpers import aio
from helpers.env import DOCKER_HOST

from asyncio_docker.client import factory


class ClientTestCase(unittest.TestCase):

    @aio.run_until_complete()
    async def test_connection(self):
        client = factory(DOCKER_HOST)(DOCKER_HOST)
        with client as session:
            pass
