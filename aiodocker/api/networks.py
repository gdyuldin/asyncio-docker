from aiohttp.hdrs import CONTENT_TYPE
from aiodocker.api.registry import APIUnbound
from aiodocker.api.errors import status_error
from aiodocker.api.constants.schemas import CREATE_NETWORK
from aiodocker.api.constants.http import (
    APPLICATION_JSON
)
from aiodocker.utils.url import build_url
from aiodocker.utils.convention import snake_case



from attrdict import AttrDict
import json


PREFIX = 'networks'


class Network(APIUnbound):

    def __init__(self, id, raw=None):
        self._id = id
        self._raw = raw

    @property
    def data(self):
        return AttrDict(snake_case(self._raw or {}))

    @property
    def raw(self):
        return AttrDict(self._raw or {})

    async def inspect(self):
        return await self.api.Networks.inspect(self.id)

    async def connect(self, container):
        return await self.api.Networks.connect(self.id, container)

    async def disconnect(self, container):
        return await self.api.Networks.disconnect(self.id, container)

    async def remove(self):
        await self.api.Networks.remove(self.id)

    @property
    def id(self):
        return self._id

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


class Networks(APIUnbound):

    @classmethod
    async def inspect(cls, id):
        req = cls.api.client.get(build_url(PREFIX, id))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return AttrDict(**await(res.json()))

    @classmethod
    async def connect(cls, id, container):

        req = cls.api.client.post(
            build_url(PREFIX, id, 'connect'),
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

    @classmethod
    async def disconnect(cls, id, container):

        req = cls.api.client.post(
            build_url(PREFIX, id, 'disconnect'),
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

    @classmethod
    async def remove(cls, id):
        req = cls.api.client.delete(build_url(PREFIX, id))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)

    @classmethod
    async def create(cls, config):
        validate(config, CREATE_NETWORK)

        req = cls.api.client.post(
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
            return cls.api.Network(snake_case(raw)['id'], raw=raw)

    @classmethod
    async def list(cls, names=None, ids=None, filters=None):
        filters = filters or {}
        if names is not None:
            filters['names'] = names

        if ids is not None:
            filters['ids'] = ids

        q = {}
        if filters:
            q['filters'] = filters

        req = cls.api.client.get(build_url(PREFIX, **q))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return [
                cls.api.Network(snake_case(raw)['id'], raw=raw) for raw in await res.json()
            ]
