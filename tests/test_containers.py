import unittest

from helpers import aio
from asyncio_docker.api import API


class ClientTestCase(unittest.TestCase):

    """
    @aio.run_until_complete()
    async def test_create_container(self, client):
        with client as session:
            api = API(session)
            await api.Container.create(config={
                'Image': 'redis:latest'
            })
    """
    pass
