import unittest
from io import BytesIO
import pathlib
import tarfile

from nose_parameterized import parameterized

from helpers import aio, fixture
from helpers.daemons import tcp_daemon
from helpers.clients import tcp_client
from fixtures.image import TEST_IMAGE

from asyncio_docker.api import RemoteAPI


TEST_IMAGE_NAME = 'asyncio_docker_test'


@aio.run_until_complete()
async def build_images(case, tags):
    image_path = pathlib.Path(__file__).parent / 'image'
    for tag in tags:
        await case.daemon.call('build', '-t',
                               '{}:{}'.format(TEST_IMAGE_NAME, tag),
                               str(image_path))


class ImageTestCase(unittest.TestCase):

    @aio.run_until_complete()
    async def setUp(self):
        self.daemon = await tcp_daemon().open()
        self.client = tcp_client().open()
        self.api = RemoteAPI(self.client)

    @parameterized.expand([
        (['foobar'],),
        (['foobar-1', 'foobar-2'],)
    ])
    @fixture.from_callable(build_images)
    @aio.run_until_complete()
    async def test_list(self, tags):
        images = await self.api.Image.list()
        self.assertEqual(len(images), 1)
        image = images[0]
        self.assertEqual(len(image.data.repo_tags), len(tags) + 1)

    @aio.run_until_complete()
    async def test_build(self):
        buf = BytesIO()
        dockerfile = str(pathlib.Path(__file__).parent / 'image' / 'Dockerfile')
        with tarfile.open(fileobj=buf, mode='w') as tar:
            tar.add(dockerfile, 'Dockerfile')
        buf.seek(0)
        image = await self.api.Image.build(buf, t=TEST_IMAGE_NAME)
        self.assertIsNotNone(image._raw)

    @aio.run_until_complete()
    async def tearDown(self):
        self.client.close()
        await self.daemon.close()
