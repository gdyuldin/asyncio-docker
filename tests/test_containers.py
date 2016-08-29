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


@aio.run_until_complete()
async def run_container_with_logs(case, data):
    cmd = "echo {stdout}; (>&2 echo {stderr})".format(**data)
    await case.daemon.call('run', '-d', '--name', 'foo', TEST_IMAGE, 'sh',  '-c', cmd)


class ContainerTestCase(unittest.TestCase):

    @aio.run_until_complete()
    async def setUp(self):
        self.daemon = await tcp_daemon().open()
        self.client = tcp_client().open()
        self.api = RemoteAPI(self.client)

    @parameterized.expand([
        (['foobar'],),
        (['foobar-1', 'foobar-2'],)
    ])
    @fixture.from_callable(run_containers)
    @aio.run_until_complete()
    async def test_list(self, names):
        containers = await self.api.Container.list()
        self.assertEqual(len(containers), len(names))
        for container in containers:
            self.assertIn(container.data.names[0][1:], names)


    @parameterized.expand([
        ({'stdout': 'foo', 'stderr': 'bar'},),
    ])
    @fixture.from_callable(run_container_with_logs)
    @aio.run_until_complete()
    async def test_logs(self, data):
        containers = await self.api.Container.list(all=True,
                                                   filters={'name': ['foo']})
        container = containers[0]
        stdout = await container.logs(stdout=True)
        self.assertIn(data['stdout'], stdout)
        stderr = await container.logs(stderr=True)
        self.assertIn(data['stderr'], stderr)



    @aio.run_until_complete()
    async def tearDown(self):
        self.client.close()
        await self.daemon.close()
