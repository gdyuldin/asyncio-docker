from aiodocker.api.registry import APIUnbound
from aiodocker.api.errors import status_error
from aiodocker.api.constants.events import CONTAINER_EVENTS, IMAGE_EVENTS

import aiohttp
import json


class Event(APIUnbound):

    @property
    def container(self):
        if self.status in CONTAINER_EVENTS:
            return self.api.Container(Id=self.id)
        else:
            return None

    def __repr__(self):
        return '%s <%s>' % (self.status, self.id)


class EventsStream(APIUnbound):

    def __init__(self, stream):
        self._stream = stream

    async def __anext__(self):
        chunk = await self._stream.readline()
        if chunk is not None:
            try:
                return self.api.Event(**json.loads(chunk.decode(encoding='UTF-8')))
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
            raise Exception
        self._res = await self.api.client.get('/events')
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self._res.close()
