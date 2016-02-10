from aiodocker.api.registry import APIUnbound
from aiodocker.api.errors import status_error
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
        pass

    async def disconnect(self, container):
        pass

    async def remove(self):
        pass

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
        pass

    @classmethod
    async def disconnect(cls, id, container):
        pass

    @classmethod
    async def remove(cls, id):
        pass

    @classmethod
    async def create(cls, config):
        pass

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

        req = cls.api.client.get(build_url(PREFIX, 'json', **q))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return [
                cls.api.Network(snake_case(val)['id'], raw=raw) for raw in await res.json()
            ]
