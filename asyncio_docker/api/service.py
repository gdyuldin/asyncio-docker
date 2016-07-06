from asyncio_docker.registry import RegistryUnbound
from asyncio_docker.collections import DataMapping
from asyncio_docker.utils.url import build_url

from .errors import status_error
from .constants.schemas import SERVICE_CONFIG
from .constants.http import APPLICATION_JSON

from aiohttp.hdrs import CONTENT_TYPE
from jsonschema import validate, ValidationError
import json


PREFIX = 'services'


class Service(RegistryUnbound):

    def __init__(self,  id, raw=None):
        self._id = id
        self._raw = raw

    @property
    def id(self):
        return self._id

    @property
    def data(self):
        return DataMapping(self._raw or {})

    async def inspect(self):
        req = self.client.get(build_url(PREFIX, self.id))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return DataMapping(await res.json())

    async def update(self, config, version=None):
        validate(config, SERVICE_CONFIG)
        if version is None:
            try:
                version = self.data.version.index
            except AttributeError:
                raise ValueError("version")

        q = {
            'version': version
        }

        req = self.client.post(
            build_url(PREFIX, self.id, 'update', **q),
            headers={
                CONTENT_TYPE: APPLICATION_JSON
            },
            data=json.dumps(config)
        )

        async with req as res:
            if res.status != 200:
                raise await status_error(res)

    async def remove(self):
        req = self.client.delete(build_url(PREFIX, self.id))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)

    @classmethod
    async def create(cls, config):
        validate(config, SERVICE_CONFIG)

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
            return cls(raw['ID'], raw=raw)

    @classmethod
    async def list(cls, id=None, name=None, filters=None):

        f = {}
        if id is not None:
            f['id'] = or_filter(id)
        if name is not None:
            f['name'] = or_filter(name)

        filters = dict(f, **(filters or {}))
        q = {}
        if filters:
            q['filters'] = filters

        req = cls.client.get(build_url(PREFIX, **q))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return [
                cls(raw['ID'], raw=raw) for raw in await res.json()
            ]

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Service):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Service):
            return self.id != other.id
        return NotImplemented

    def __repr__(self):
        return 'Service <%s>' % self.id

    def __str__(self):
        return self.id
