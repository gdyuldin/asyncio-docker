from aiodocker.api.registry import APIUnbound
from aiodocker.api.errors import status_error
from aiodocker.api.constants.events import CONTAINER_EVENTS, IMAGE_EVENTS

import aiohttp
import json


class Event(APIUnbound):

    def __init__(self, id, *, status, time, fromm):
        self._id = id
        self._status = status
        self._time = time
        self._fromm = fromm

    @property
    def id(self):
        return self._id

    @property
    def status(self):
        return self._status

    @property
    def time(self):
        return self._time

    @property
    def fromm(self):
        return self._fromm

    @property
    def container(self):
        if self.status in CONTAINER_EVENTS:
            return self.api.Container(self.id)
        else:
            return None

    @property
    def image(self):
        if self.status in IMAGE_EVENTS:
            return self.api.Image(self.id)
        else:
            return None

    def __hash__(self):
        return hash((self.status, self.id, self.time, self.fromm))

    def __eq__(self, other):
        if isinstance(other, Event):
            return hash(self) == hash(other)
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Image):
            return hash(self) != hash(other)
        return NotImplemented

    def __repr__(self):
        return 'Event <%s:%s at %s>' % (self.id, self.status, self.time)

    def __str__(self):
        return self.id


class EventsStream(APIUnbound):

    def __init__(self, stream):
        self._stream = stream

    async def __anext__(self):
        chunk = await self._stream.readline()
        if chunk is not None:
            try:
                data = json.loads(chunk.decode(encoding='UTF-8'))
                return self.api.Event(
                    data['id'],
                    status=data['status'],
                    time=data['time'],
                    fromm=data['from']
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
        res = await self.api.client.get('/events')
        if res.status != 200:
            raise await status_error(res)

        self._res = res
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self._res.close()
