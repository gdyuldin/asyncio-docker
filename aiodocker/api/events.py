from aiodocker.api.registry import APIUnbound
from aiodocker.api.errors import status_error
from aiodocker.api.constants.types import CONTAINER, IMAGE, NETWORK, VOLUME
from aiodocker.utils.convention import snake_case

from attrdict import AttrDict
import aiohttp
import json


class Event(APIUnbound):

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
            return self.api.Container(self.actor.id)
        else:
            return None

    @property
    def image(self):
        if self.type == IMAGE:
            return self.api.Image(self.actor.id)
        else:
            return None

    @property
    def network(self):
        if self.type == NETWORK:
            return self.api.Network(self.actor.id)
        else:
            return None

    @property
    def volume(self):
        if self.type == VOLUME:
            return self.api.Volume(self.actor.id)
        else:
            return None

    @property
    def raw(self):
        return AttrDict(self._raw or {})

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


class EventsStreamReponse(aiohttp.ClientResponse):

    flow_control_class = aiohttp.FlowControlChunksQueue


class EventsStream(APIUnbound):

    def __init__(self, stream):
        self._stream = stream

    async def __anext__(self):
        chunk = await self._stream.read()
        if chunk is not None:
            try:
                raw = json.loads(chunk.decode(encoding='UTF-8'))
                data = snake_case(raw)
                return self.api.Event(
                    action=data['action'],
                    type=data['type'],
                    actor=data['actor'],
                    time=data['time_nano'],
                    raw=raw,
                )

            except json.JSONDecodeError:
                raise StopAsyncIteration


class Events(APIUnbound):

    def __init__(self, since=None, until=None):
        self._res = None

    @classmethod
    def get(cls):
        return cls.api.Events()

    async def __aiter__(self):
        return self.api.EventsStream(self._res.content)

    async def __aenter__(self):
        if self._res is not None:
            raise Exception()
        res = await self.api.client.get('/events', response_class=EventsStreamReponse)
        if res.status != 200:
            raise await status_error(res)
        self._res = res
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self._res.close()
