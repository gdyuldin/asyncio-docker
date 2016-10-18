from io import BytesIO
import pathlib
import tarfile
import unittest

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
async def run_container_with_cmd(case, cmd):
    await case.daemon.call('run', '-d', '--name', 'foo', TEST_IMAGE, 'sh',  '-c', cmd)


@aio.run_until_complete()
async def create_container(case):
    await case.daemon.call('create', '--name', 'foo', TEST_IMAGE, 'ls', '/tmp')


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
        ("echo 'foo'; (>&2 echo 'bar')",),
    ])
    @fixture.from_callable(run_container_with_cmd)
    @aio.run_until_complete()
    async def test_logs(self, cmd):
        container = (await self.api.Container.list(all=True,
                                                   filters={'name': ['foo']}))[0]
        stdout = await container.logs(stdout=True)
        self.assertIn('foo', stdout.decode())
        stderr = await container.logs(stderr=True)
        self.assertIn('bar', stderr.decode())


    @fixture.from_callable(create_container)
    @aio.run_until_complete()
    async def test_put_archive(self):
        container = (await self.api.Container.list(all=True,
                                                   filters={'name': ['foo']}))[0]
        buf = BytesIO()
        cur_file = pathlib.Path(__file__)
        content_dir = str(cur_file.parent)
        with tarfile.open(fileobj=buf, mode='w') as tar:
            tar.add(content_dir, '')
        buf.seek(0)
        await container.put_archive('/tmp', buf)
        await self.daemon.call('start', container.id)
        await self.daemon.call('wait', container.id)
        _, stdout, _ = await self.daemon.call('logs', container.id)
        self.assertIn(cur_file.name, stdout.decode())

    @parameterized.expand([
        ("sleep 5",),
    ])
    @fixture.from_callable(run_container_with_cmd)
    @aio.run_until_complete()
    async def test_wait(self, data):
        containers = await self.api.Container.list(all=True,
                                                   filters={'name': ['foo']})
        container = containers[0]
        container_data = await container.inspect()
        self.assertTrue(container_data['State']['Running'])
        result = await container.wait()
        self.assertEqual(result.status_code, 0)
        container_data = await container.inspect()
        self.assertFalse(container_data['State']['Running'])

    @aio.run_until_complete()
    async def tearDown(self):
        self.client.close()
        await self.daemon.close()
