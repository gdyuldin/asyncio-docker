from asyncio_docker.registry import RegistryUnbound
from asyncio_docker.collections import DataMapping
from asyncio_docker.utils.url import build_url

from .errors import status_error
from .constants.http import APPLICATION_JSON, APPLICATION_VND_DOCKER_RAW_STREAM

from aiohttp import EofStream
from aiohttp.hdrs import CONTENT_TYPE

import struct
import json


PREFIX = 'exec'


class ExecInstance(RegistryUnbound):

    def __init__(self,  id, raw=None):
        self._id = id
        self._raw = raw

    @property
    def id(self):
        return self._id

    @property
    def data(self):
        return DataMapping(self._raw or {})

    def exec_start(self, detach=False, tty=False):

        data = {
            'Detach': detach,
            'Tty': tty
        }

        req = self.client.post(
            build_url('exec', self.id, 'start'),
            headers={
                CONTENT_TYPE: APPLICATION_JSON
            },
            data=json.dumps(data)
        )

        return self.registry.ExecStream(req, tty=tty)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, ExecInstance):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, ExecInstance):
            return self.id != other.id
        return NotImplemented

    def __repr__(self):
        return 'ExecInstance <%s>' % self.id

    def __str__(self):
        return self.id


class ExecStream(RegistryUnbound):

    def __init__(self, req, tty=False):
        self._req = req
        self._tty = tty

    async def __aenter__(self):
        if hasattr(self, '_res'):
            raise RuntimeError("Stream is in use.")
        res = await self._req
        if res.status != 200:
            raise await status_error(res)
        self._res = res
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self._res.close()
        del self._res

    async def __aiter__(self):
        return self

    async def write(self, data):
        self._res.connection.writer.write(data)
        await self._res.connection.writer.drain()

    async def __anext__(self):
        content_type = self._res.headers[CONTENT_TYPE]
        try:
            typ = 1
            if not self._tty:
                header = await self._res.content.read(8)
                if not header:
                    raise StopAsyncIteration
                typ, length = struct.unpack('>BxxxL', header)
                data = await self._res.content.read(length)
            else:
                data = await self._res.content.readany()
                if not data:
                    raise StopAsyncIteration

            typ = {
                0: 'stdin',
                1: 'stdout',
                2: 'stderr'
            }.get(typ, None)

            if content_type == APPLICATION_VND_DOCKER_RAW_STREAM:
                return {
                    'type': typ,
                    'msg': str(data, 'utf-8')
                }
            elif content_type == APPLICATION_JSON:
                return {
                    'type': typ,
                    'payload': json.loads(str(data, 'utf-8'))
                }
            else:
                return {
                    'type': typ,
                    'raw': str(data, 'utf-8')
                }

        except EofStream:
            raise StopAsyncIteration
