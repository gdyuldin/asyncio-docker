import unittest
import asyncio

from nose_parameterized import parameterized

from helpers import aio, fixture
from helpers.daemons import tcp_daemon
from helpers.clients import tcp_client
from fixtures.image import TEST_IMAGE

from asyncio_docker.api import RemoteAPI


@aio.run_until_complete()
async def run_containers(case, names):
    for name in names:
        await case.daemon.call('run', '-t', '-d', '--name', name, TEST_IMAGE, 'sh')


class ContainerTestCase(unittest.TestCase):

    @aio.run_until_complete(30)
    async def setUp(self):
        self.daemon = await tcp_daemon().open()
        self.client = tcp_client().open()
        self.api = RemoteAPI(self.client)

    @parameterized.expand([
        (['foobar'],),
        (['foobar-1', 'foobar-2'],)
    ])
    @fixture.from_callable(run_containers)
    @aio.run_until_complete(30)
    async def test_list(self, names):
        containers = await self.api.Container.list()
        self.assertEqual(len(containers), len(names))
        for container in containers:
            self.assertIn(container.data.names[0][1:], names)


    @aio.run_until_complete(30)
    async def tearDown(self):
        self.client.close()
        await self.daemon.clean()
        await self.daemon.close()
