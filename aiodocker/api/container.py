from aiodocker.registry import RegistryUnbound
from aiodocker.api.errors import status_error
from aiodocker.api.constants.schemas import CREATE_CONTAINER
from aiodocker.api.constants.http import (
    APPLICATION_JSON
)
from aiodocker.utils.convention import snake_case
from aiodocker.utils.url import build_url

from aiohttp.hdrs import CONTENT_TYPE
from attrdict import AttrDict
from jsonschema import validate, ValidationError
import json


PREFIX = 'containers'


class Container(RegistryUnbound):

    def __init__(self,  id, raw=None):
        self._id = id
        self._raw = raw

    @property
    def data(self):
        return AttrDict(snake_case(self._raw or {}))

    @property
    def raw(self):
        return AttrDict(self._raw or {})

    @property
    def id(self):
        return self._id

    async def top(self):
        req = self.client.get(build_url(PREFIX, self.id, 'top'))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return AttrDict(**(await res.json()))

    async def inspect(self):
        req = self.client.get(build_url(PREFIX, self.id, 'json'))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return AttrDict(**(await res.json()))

    async def stop(self, timeout=None):
        req = self.client.post(build_url(PREFIX, self.id, 'stop'))
        async with req as res:
            if res.status != 204:
                raise await status_error(res)

    async def start(self):
        req = self.client.post(build_url(PREFIX, self.id, 'start'))
        async with req as res:
            if res.status != 204:
                raise await status_error(res)

    async def restart(self, timeout=None):
        req = self.client.post(build_url(PREFIX, self.id, 'restart'))
        async with req as res:
            if res.status != 204:
                raise await status_error(res)

    async def pause(self):
        req = self.client.post(build_url(PREFIX, self.id, 'pause'))
        async with req as res:
            if res.status != 204:
                raise await status_error(res)

    async def unpause(self):
        req = self.client.post(build_url(PREFIX, self.id, 'unpause'))
        async with req as res:
            if res.status != 204:
                raise await status_error(res)

    async def kill(self, signal=None):
        req = self.client.post(build_url(PREFIX, self.id, 'kill'))
        async with req as res:
            if res.status != 204:
                raise await status_error(res)

    async def remove(self, remove_volumes=None, force=None):
        req = self.client.delete(build_url(PREFIX, self.id))
        async with req as res:
            if res.status != 204:
                raise await status_error(res)

    async def exec_create(self, *cmd, attach_stdin=False, attach_stdout=True,
            attach_stderr=True, tty=False, detach_keys='crtl-c'):

        data = {
            'Cmd': [str(x) for x in cmd],
            'AttachStdin': attach_stdin,
            'AttachStdout': attach_stdout,
            'AttachStderr': attach_stderr,
            'Tty': tty,
            'DetachKeys': detach_keys
        }

        req = self.client.post(
            build_url(PREFIX, self.id, 'exec'),
            headers={
                CONTENT_TYPE: APPLICATION_JSON
            },
            data=json.dumps(data)
        )

        async with req as res:
            if res.status != 201:
                raise await status_error(res)

            raw = await(res.json())
            return self.registry.ExecInstance(snake_case(raw)['id'], raw=raw)

    @classmethod
    async def create(cls, config, name=None):
        validate(config, CREATE_CONTAINER)

        q = {}
        if name is not None:
            q['name'] = name

        req = cls.client.post(
            build_url(PREFIX, 'create', **q),
            headers={
                CONTENT_TYPE: APPLICATION_JSON
            },
            data=json.dumps(config)
        )

        async with req as res:
            if res.status != 201:
                raise await status_error(res)

            raw = await(res.json())
            return cls(snake_case(raw)['id'], raw=raw)

    @classmethod
    async def list(cls, all=None, labels=None, filters=None):
        filters = filters or {}
        for label, val in (labels or {}).items():
            filters['label'] = filters.get('label', []) + [
                '%s=%s' % (label, val) if val else label
            ]

        q = {}
        if filters:
            q['filters'] = filters

        if all is not None:
            q['all'] = '1' if all else '0'

        req = cls.client.get(build_url(PREFIX, 'json', **q))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return [
                cls(snake_case(raw)['id'], raw=raw) for raw in await res.json()
            ]

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Container):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Container):
            return self.id != other.id
        return NotImplemented

    def __repr__(self):
        return 'Container <%s>' % self.id

    def __str__(self):
        return self.id


class ExecInstance(RegistryUnbound):

    def __init__(self,  id, raw=None):
        self._id = id
        self._raw = raw

    def exec_start(self, detach=False, tty=False):

        data = {
            'Detach': detach,
            'Tty': tty
        }

        req = self.client.post(
            build_url('exec', self.id, 'start'),
            headers={
                CONTENT_TYPE: APPLICATION_JSON
            },
            data=json.dumps(data)
        )

        return self.registry.ExecStream(req)

    @property
    def data(self):
        return AttrDict(snake_case(self._raw or {}))

    @property
    def raw(self):
        return AttrDict(self._raw or {})

    @property
    def id(self):
        return self._id

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, ExecInstance):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, ExecInstance):
            return self.id != other.id
        return NotImplemented

    def __repr__(self):
        return 'ExecInstance <%s>' % self.id

    def __str__(self):
        return self.id


class ExecStream(RegistryUnbound):

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
        header = await self._res.content.read(8)
        if header is not None:
            return ''
