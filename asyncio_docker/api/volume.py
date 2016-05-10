from aiohttp.hdrs import CONTENT_TYPE
from asyncio_docker.registry import RegistryUnbound
from asyncio_docker.api.errors import status_error
from asyncio_docker.api.constants.schemas import CREATE_VOLUME
from asyncio_docker.api.constants.http import (
    APPLICATION_JSON
)
from asyncio_docker.utils.url import build_url
from asyncio_docker.utils.convention import snake_case



from attrdict import AttrDict
import json


PREFIX = 'volumes'


class Volume(RegistryUnbound):

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
        req = self.client.get(build_url(PREFIX, self.name))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return AttrDict(**await(res.json()))

    async def remove(self):
        req = self.client.delete(build_url(PREFIX, self.name))
        async with req as res:
            if res.status != 204:
                raise await status_error(res)

    @classmethod
    async def create(cls, config):
        validate(config, CREATE_VOLUME)

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
            return cls(snake_case(raw)['name'], raw=raw)

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
                cls(snake_case(raw)['name'], raw=raw)
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
