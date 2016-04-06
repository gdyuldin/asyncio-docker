from aiohttp.hdrs import CONTENT_TYPE
from aiodocker.api.registry import APIUnbound
from aiodocker.api.errors import status_error
from aiodocker.api.constants.schemas import CREATE_CONTAINER
from aiodocker.api.constants.http import (
    APPLICATION_JSON
)
from aiodocker.utils.convention import snake_case
from aiodocker.utils.url import build_url

from attrdict import AttrDict
from jsonschema import validate, ValidationError
import json


PREFIX = 'containers'


class Container(APIUnbound):

    def __init__(self,  id, raw=None):
        self._id = id
        self._raw = raw

    @property
    def data(self):
        return AttrDict(snake_case(self._raw or {}))

    @property
    def raw(self):
        return AttrDict(self._raw or {})

    async def top(self):
        return await self.api.Containers.top(self.id)

    async def inspect(self):
        return await self.api.Containers.inspect(self.id)

    async def start(self):
        return await self.api.Containers.start(self.id)

    async def stop(self):
        return await self.api.Containers.stop(self.id)

    async def restart(self):
        return await self.api.Containers.restart(self.id)

    async def pause(self):
        return await self.api.Containers.pause(self.id)

    async def unpause(self):
        return await self.api.Containers.unpause(self.id)

    async def kill(self):
        return await self.api.Containers.kill(self.id)

    async def remove(self):
        return await self.api.Containers.remove(self.id)

    @property
    def id(self):
        return self._id

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Container):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Container):
            return self.id != other.id
        return NotImplemented

    def __repr__(self):
        return 'Container <%s>' % self.id

    def __str__(self):
        return self.id


class Containers(APIUnbound):

    @classmethod
    async def top(cls, id):
        req = cls.api.client.get(build_url(PREFIX, id, 'top'))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return AttrDict(**(await res.json()))

    @classmethod
    async def inspect(cls, id):
        req = cls.api.client.get(build_url(PREFIX, id, 'json'))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return AttrDict(**(await res.json()))

    @classmethod
    async def stop(cls, id, timeout=None):
        req = cls.api.client.post(build_url(PREFIX, id, 'stop'))
        async with req as res:
            if res.status != 204:
                raise await status_error(res)

    @classmethod
    async def start(cls, id):
        req = cls.api.client.post(build_url(PREFIX, id, 'start'))
        async with req as res:
            if res.status != 204:
                raise await status_error(res)

    @classmethod
    async def restart(cls, id, timeout=None):
        req = cls.api.client.post(build_url(PREFIX, id, 'restart'))
        async with req as res:
            if res.status != 204:
                raise await status_error(res)

    @classmethod
    async def pause(cls, id):
        req = cls.api.client.post(build_url(PREFIX, id, 'pause'))
        async with req as res:
            if res.status != 204:
                raise await status_error(res)

    @classmethod
    async def unpause(cls, id):
        req = cls.api.client.post(build_url(PREFIX, id, 'unpause'))
        async with req as res:
            if res.status != 204:
                raise await status_error(res)

    @classmethod
    async def kill(cls, id, signal=None):
        req = cls.api.client.post(build_url(PREFIX, id, 'kill'))
        async with req as res:
            if res.status != 204:
                raise await status_error(res)

    @classmethod
    async def remove(cls, id, remove_volumes=None, force=None):
        req = cls.api.client.delete(build_url(PREFIX, id))
        async with req as res:
            if res.status != 204:
                raise await status_error(res)

    @classmethod
    async def create(cls, config, name=None):
        validate(config, CREATE_CONTAINER)

        q = {}
        if name is not None:
            q['name'] = name

        req = cls.api.client.post(
            build_url(PREFIX, 'create', **q),
            headers={
                CONTENT_TYPE: APPLICATION_JSON
            },
            data=json.dumps(config)
        )

        async with req as res:
            if res.status != 201:
                raise await status_error(res)

            raw = await(res.json())
            return cls.api.Container(snake_case(raw)['id'], raw=raw)

    @classmethod
    async def list(cls, all=None, labels=None, filters=None):
        filters = filters or {}
        for label, val in (labels or {}).items():
            filters['label'] = filters.get('label', []) + [
                '%s=%s' % (label, val) if val else label
            ]

        q = {}
        if filters:
            q['filters'] = filters

        if all is not None:
            q['all'] = '1' if all else '0'

        req = cls.api.client.get(build_url(PREFIX, 'json', **q))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return [
                cls.api.Container(snake_case(raw)['id'], raw=raw) for raw in await res.json()
            ]
