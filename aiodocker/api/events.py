import aiohttp
import json
from json.decoder import JSONDecodeError

from .registry import APIUnbound
from .json import JSONRoot
from .errors import status_error


ATTACH = 'attach'
COMMIT = 'commit'
COPY = 'copy'
CREATE = 'create'
DESTROY = 'destroy'
DIE = 'die'
EXEC_CREATE = 'exec_create'
EXEC_START = 'exec_start'
EXPORT = 'export'
KILL = 'kill'
OOM = 'oom'
PAUSE = 'pause'
RENAME = 'rename'
RESIZE = 'resize'
RESTART = 'restart'
START = 'start'
STOP = 'stop'
TOP = 'top'
UNPAUSE = 'unpause'

DELETE = 'delete'
IMPORT = 'import'
PULL = 'pull'
PUSH = 'push'
TAG = 'tag'
UNTAG = 'untag'


_container_events = (
    ATTACH,
    COMMIT,
    COPY,
    CREATE,
    DESTROY,
    DIE,
    EXEC_CREATE,
    EXEC_START,
    EXPORT,
    KILL,
    OOM,
    PAUSE,
    RENAME,
    RESIZE,
    RESTART,
    START,
    STOP,
    TOP,
    UNPAUSE
)

_image_events = (
    DELETE,
    IMPORT,
    PULL,
    PUSH,
    TAG,
    UNTAG
)


class Event(JSONRoot, APIUnbound):

    def __init__(self, json):
        self._json = json

    def get_json(self):
        return self._json

    @property
    def container(self):
        return self.api.Container(Id=self.id)

    def __repr__(self):
        return '%s <%s>' % (self.status, self.id)


class EventsStream(APIUnbound):

    def __init__(self, stream):
        self._stream = stream

    async def __anext__(self):
        chunk = await self._stream.readline()
        if chunk is not None:
            try:
                text = chunk.decode(encoding='UTF-8')
                return self.api.Event(json.loads(text))
            except JSONDecodeError:
                raise StopAsyncIteration


class Events(APIUnbound):

    def __init__(self, since=None, until=None):
        self._response = None

    @classmethod
    def get(cls):
        return cls.api.Events()

    async def __aiter__(self):
        return self.api.EventsStream(self._response.content)

    async def __aenter__(self):
        if self._response is not None:
            raise Exception
        self._response = await self.api.client.get('/events')
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self._response.close()
