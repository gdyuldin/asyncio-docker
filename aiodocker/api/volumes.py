from aiohttp.hdrs import CONTENT_TYPE
from aiodocker.api.registry import APIUnbound
from aiodocker.api.errors import status_error
from aiodocker.api.constants.http import (
    APPLICATION_JSON
)
from aiodocker.utils.url import build_url
from aiodocker.utils.convention import snake_case



from attrdict import AttrDict
import json


PREFIX = 'volumes'


class Volume(APIUnbound):

    def __init__(self, name, raw=None):
        self._name = name
        self._raw = raw

    @property
    def data(self):
        return AttrDict(snake_case(self._raw or {}))

    @property
    def raw(self):
        return AttrDict(self._raw or {})

    async def inspect(self):
        return await self.api.Volumes.inspect(self.name)

    async def remove(self):
        await self.api.Volumes.remove(self.name)

    @property
    def name(self):
        return self._name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, Volume):
            return self.name == other.name
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Volume):
            return self.name != other.name
        return NotImplemented

    def __repr__(self):
        return 'Volume <%s>' % self.name

    def __str__(self):
        return self.name


class Volumes(APIUnbound):

    @classmethod
    async def inspect(cls, name):
        req = cls.api.client.get(build_url(PREFIX, name))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return AttrDict(**await(res.json()))

    @classmethod
    async def remove(cls, name):
        pass

    @classmethod
    async def create(cls, config):
        pass

    @classmethod
    async def list(cls, dangling=False, filters=None):
        filters = filters or {}
        if dangling:
            filters['dangling'] = True

        q = {}
        if filters:
            q['filters'] = filters

        req = cls.api.client.get(build_url(PREFIX, **q))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return [
                cls.api.Volume(snake_case(raw)['name'], raw=raw) for raw in await res.json()
            ]
