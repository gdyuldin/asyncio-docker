from asyncio_docker.registry import RegistryUnbound
from asyncio_docker.collections import DataMapping
from asyncio_docker.utils.url import build_url

from .errors import status_error
from .constants.schemas import VOLUME_CONFIG
from .constants.http import APPLICATION_JSON

from aiohttp.hdrs import CONTENT_TYPE
import json


PREFIX = 'volumes'


class Volume(RegistryUnbound):

    def __init__(self, name, raw=None):
        self._name = name
        self._raw = raw

    @property
    def data(self):
        return DataMapping(self._raw or {})

    async def inspect(self):
        req = self.client.get(build_url(PREFIX, self.name))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return DataMapping(await res.json())

    async def remove(self):
        req = self.client.delete(build_url(PREFIX, self.name))
        async with req as res:
            if res.status != 204:
                raise await status_error(res)

    @classmethod
    async def create(cls, config):
        validate(config, VOLUME_CONFIG)

        req = cls.client.post(
            build_url(PREFIX, 'create'),
            headers={
                CONTENT_TYPE: APPLICATION_JSON
            },
            data=json.dumps(config)
        )

        async with req as res:
            if res.status != 201:
                raise await status_error(res)

            raw = await(res.json())
            return cls(raw['Name'], raw=raw)

    @classmethod
    async def list(cls, dangling=False, filters=None):
        filters = filters or {}
        if dangling:
            filters['dangling'] = True

        q = {}
        if filters:
            q['filters'] = filters

        req = cls.client.get(build_url(PREFIX, **q))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return [
                cls(raw['Name'], raw=raw)
                for raw in ((await res.json()).get('Volumes', None) or [])
            ]

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
