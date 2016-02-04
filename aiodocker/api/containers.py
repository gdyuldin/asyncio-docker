from aiodocker.api.registry import APIUnbound
from aiodocker.api.errors import status_error
from aiodocker.api.constants.schemas import CONFIG
from aiodocker.api.constants.http import (
    HEADER_CONTENT_TYPE,
    APPLICATION_JSON
)
from aiodocker.utils.schemas import schema_extract
from aiodocker.utils.url import build_url

import json
from jsonschema import validate, ValidationError


PREFIX = 'containers'


class Container(APIUnbound):

    def __init__(self, id):
        self._id = id

    def top(self):
        return self.api.Containers.top(self.Id)

    def inspect(self):
        return self.api.Containers.inspect(self.Id)

    def start(self):
        return self.api.Containers.start(self.Id)

    def stop(self):
        return self.api.Containers.stop(self.Id)

    def restart(self):
        return self.api.Containers.restart(self.Id)

    def pause(self):
        return self.api.Containers.pause(self.Id)

    def unpause(self):
        return self.api.Containers.unpause(self.Id)

    def kill(self):
        return self.api.Containers.kill(self.Id)

    def remove(self):
        return self.api.Containers.remove(self.Id)

    @property
    def Id(self):
        return self._id

    def __hash__(self):
        return hash(self.Id)

    def __eq__(self, other):
        if isinstance(other, Container):
            return self.Id == other.Id
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Container):
            return self.Id != other.Id
        return NotImplemented

    def __repr__(self):
        return 'Container <%s>' % self.Id

    def __str__(self):
        return self.Id


class Containers(APIUnbound):

    @classmethod
    async def top(cls, id):
        req = cls.api.client.get(build_url(PREFIX, id, 'top'))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return await res.json()

    @classmethod
    async def inspect(cls, id):
        req = cls.api.client.get(build_url(PREFIX, id, 'json'))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return cls.api.Container(**await(res.json()))

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
        config = schema_extract(config, CONFIG)
        validate(config, CONFIG)

        q = {}
        if name is not None:
            q['name'] = name

        req = cls.api.client.post(
            build_url(PREFIX, id, 'create', **q),
            headers={
                HEADER_CONTENT_TYPE: APPLICATION_JSON
            },
            data=json.dumps(config)
        )

        async with req as res:
            if res.status != 201:
                raise await status_error(res)
            return cls.api.Container((await(res.json()))['Id'])

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
                cls.api.Container(data['Id']) for data in await res.json()
            ]
