from asyncio_docker.registry import RegistryUnbound
from asyncio_docker.collections import DataMapping
from asyncio_docker.utils.url import build_url

from .errors import status_error
from .constants.schemas import NETWORK_CONFIG
from .constants.http import APPLICATION_JSON

from aiohttp.hdrs import CONTENT_TYPE
import json


PREFIX = 'networks'


class Network(RegistryUnbound):

    def __init__(self, id, raw=None):
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

    async def connect(self, container):
        req = self.client.post(
            build_url(PREFIX, self.id, 'connect'),
            headers={
                CONTENT_TYPE: APPLICATION_JSON
            },
            data=json.dumps({
                'container': container.id
            })
        )

        async with req as res:
            if res.status != 200:
                raise await status_error(res)

    async def disconnect(self, container):
        req = self.client.post(
            build_url(PREFIX, self.id, 'disconnect'),
            headers={
                CONTENT_TYPE: APPLICATION_JSON
            },
            data=json.dumps({
                'container': container.id
            })
        )

        async with req as res:
            if res.status != 200:
                raise await status_error(res)

    async def remove(self):
        req = self.client.delete(build_url(PREFIX, self.id))
        async with req as res:
            if res.status != 204:
                raise await status_error(res)

    @classmethod
    async def create(cls, config):
        validate(config, NETWORK_CONFIG)

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
            return cls(raw['Id'], raw=raw)

    @classmethod
    async def list(cls, names=None, ids=None, filters=None):

        f = {}
        if names is not None:
            f['names'] = names

        if ids is not None:
            f['ids'] = ids

        filters = dict(f, **(filters or {}))
        q = {}
        if filters:
            q['filters'] = filters

        req = cls.client.get(build_url(PREFIX, **q))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return [
                cls(raw['Id'], raw=raw) for raw in await res.json()
            ]

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Network):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Network):
            return self.id != other.id
        return NotImplemented

    def __repr__(self):
        return 'Network <%s>' % self.id

    def __str__(self):
        return self.id
