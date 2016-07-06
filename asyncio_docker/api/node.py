from asyncio_docker.registry import RegistryUnbound
from asyncio_docker.collections import DataMapping
from asyncio_docker.utils.url import build_url
from asyncio_docker.utils.filters import or_filter

from .errors import status_error
from .constants.node_memberships import (
    PENDING,
    ACCEPTED,
    REJECTED
)

from .constants.node_roles import (
    MANAGER,
    WORKER
)


PREFIX = 'nodes'


class Node(RegistryUnbound):

    def __init__(self,  id, raw=None):
        self._id = id
        self._raw = raw

    @property
    def data(self):
        return DataMapping(self._raw or {})

    @property
    def id(self):
        return self._id

    async def inspect(self):
        req = self.client.get(build_url(PREFIX, self.id))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return DataMapping(await res.json())

    @classmethod
    async def list(cls, id=None, name=None, membership=None, role=None,
            filters=None):

        f = {}
        if id is not None:
            f['id'] = or_filter(id)
        if name is not None:
            f['name'] = or_filter(name)
        if membership is not None:
            if membership not in [PENDING, ACCEPTED, REJECTED]:
                raise ValueError(membership)
            f['membership'] = or_filter(membership)
        if role is not None:
            if role not in [MANAGER, WORKER]:
                raise ValueError(role)
            f['role'] = or_filter(role)

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
        if isinstance(other, Node):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Node):
            return self.id != other.id
        return NotImplemented

    def __repr__(self):
        return 'Node <%s>' % self.id

    def __str__(self):
        return self.id
