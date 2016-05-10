from asyncio_docker.registry import RegistryUnbound
from asyncio_docker.api.errors import status_error
from asyncio_docker.api.constants.types import CONTAINER, IMAGE, NETWORK, VOLUME
from asyncio_docker.utils.convention import snake_case

from attrdict import AttrDict
import aiohttp
import json


class Event(RegistryUnbound):

    def __init__(self, *, action, type, actor, time, raw=None):
        self._action = action
        self._type = type
        self._actor = actor
        self._time = time
        self._raw = raw

    @property
    def action(self):
        return self._action

    @property
    def type(self):
        return self._type

    @property
    def actor(self):
        return AttrDict(self._actor)

    @property
    def time(self):
        return self._time

    @property
    def container(self):
        if self.type == CONTAINER:
            return self.registry.Container(self.actor.id)
        else:
            return None

    @property
    def image(self):
        if self.type == IMAGE:
            return self.registry.Image(self.actor.id)
        else:
            return None

    @property
    def network(self):
        if self.type == NETWORK:
            return self.registry.Network(self.actor.id)
        else:
            return None

    @property
    def volume(self):
        if self.type == VOLUME:
            return self.registry.Volume(self.actor.id)
        else:
            return None

    @property
    def raw(self):
        return AttrDict(self._raw or {})

    @classmethod
    def get(cls, since=None, until=None):
         req = cls.registry.client.get('/events')
         return cls.registry.EventStream(req)

    def __hash__(self):
        return hash((self.action, self.type, self.time))

    def __eq__(self, other):
        if isinstance(other, Event):
            return hash(self) == hash(other)
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Image):
            return hash(self) != hash(other)
        return NotImplemented

    def __repr__(self):
        return 'Event <%s:%s at %s>' % (self.action, self.type, self.time)

    def __str__(self):
        return self.action



class EventStream(RegistryUnbound):

    def __init__(self, req):
        self._req = req

    async def __aenter__(self):
        if hasattr(self, '_res'):
            raise Exception("Stream is in use.")
        res = await self._req
        if res.status != 200:
            raise await status_error(res)
        self._res = res
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self._res.close()
        del self._res

    async def __aiter__(self):
        return self

    async def __anext__(self):
        chunk = await self._res.content.readany()
        if chunk is not None:
            try:
                raw = json.loads(chunk.decode(encoding='UTF-8'))
                data = snake_case(raw)
                return self.registry.Event(
                    action=data['action'],
                    type=data['type'],
                    actor=data['actor'],
                    time=data['time_nano'],
                    raw=raw,
                )
            except json.JSONDecodeError as ex:
                raise StopAsyncIteration
