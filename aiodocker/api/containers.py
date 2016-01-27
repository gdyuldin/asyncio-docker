from aiodocker.api.base import BaseEntity
from aiodocker.api.registry import APIUnbound
from aiodocker.api.errors import status_error
from aiodocker.api.constants.schemas import CONFIG
from aiodocker.utils.schemas import schema_extract
from aiodocker.utils.query import query_string

import json
from jsonschema import validate, ValidationError


class Container(BaseEntity, APIUnbound):

    async def top(self):
        req = self.api.client.get(self._url('top'))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return await res.json()

    async def inspect(self):
        req = self.api.client.get(self._url('json'))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return self.api.Container(**await(res.json()))

    async def stop(self, timeout=None):
        req = self.api.client.post(self._url('stop'))
        async with req as res:
            if res.status != 204:
                raise await status_error(res)

    async def start(self):
        req = self.api.client.post(self._url('start'))
        async with req as res:
            if res.status != 204:
                raise await status_error(res)

    async def restart(self, timeout=None):
        req = self.api.client.post(self._url('restart'))
        async with req as res:
            if res.status != 204:
                raise await status_error(res)

    async def pause(self):
        req = self.api.client.post(self._url('pause'))
        async with req as res:
            if res.status != 204:
                raise await status_error(res)

    async def unpause(self):
        req = self.api.client.post(self._url('unpause'))
        async with req as res:
            if res.status != 204:
                raise await status_error(res)

    async def kill(self, signal=None):
        req = self.api.client.post(self._url('kill'))
        async with req as res:
            if res.status != 204:
                raise await status_error(res)

    async def remove(self, remove_volumes=None, force=None):
        req = self.api.client.delete(self._url())
        async with req as res:
            if res.status != 204:
                raise await status_error(res)

    async def create(self, name=None):
        if 'Config' in self:
            Config = self.Config
        else:
            Config = dict(self)

        Config = schema_extract(Config, CONFIG)
        validate(Config, CONFIG)

        q = {}
        if name is not None:
            q['name'] = name

        req = self.api.client.post(
            '/containers/create%s' % query_string(**q),
            headers={
                'Content-Type': 'application/json'
            },
            data=json.dumps(Config)
        )

        async with req as res:
            if res.status != 201:
                raise await status_error(res)
            return self.api.Container(**await(res.json()))

    def _url(self, action=None):
        if action is None:
            return '/containers/%s' % self._require_Id()
        else:
            return '/containers/%s/%s' % (self._require_Id(), action)

    def _require_Id(self):
        if 'Id' not in self:
            raise Exception("Id is required")
        return self.Id

    def __hash__(self):
        if 'Id' in self:
            return hash(self.Id)
        else:
            return super(Container, self).__hash__()

    def __eq__(self, other):
        if isinstance(other, Container) and 'Id' in self and 'Id' in other:
            return self.Id == other.Id
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Container) and 'Id' in self and 'Id' in other:
            return self.Id != other.Id
        return NotImplemented

    def __repr__(self):
        if 'Id' in self:
            return 'Container <%s>' % self.Id
        else:
            return 'Container <unknown>'

    def __str__(self):
        if 'Id' in self:
            return self.Id
        else:
            return "unknown"


class Containers(list, APIUnbound):

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

        req = cls.api.client.get('/containers/json%s' % query_string(**q))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return cls.api.Containers([
                cls.api.Container(**val) for val in await res.json()
            ])
