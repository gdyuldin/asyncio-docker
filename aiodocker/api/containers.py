from .registry import APIUnbound
from .json import JSONRoot
from .errors import status_error

import json


class Container(JSONRoot, APIUnbound):

    def __init__(self, json=None, *, Id=None):
        if json is None and Id is None:
            raise ValueError()

        self._json = json or {}
        if Id is not None:
            self.Id = Id

    def get_json(self):
        return self._json

    async def top(self):
        async with self.api.client.get('/containers/%s/top' % self.Id) as r:
            if r.status != 200:
                raise status_error(r.status)
            return await r.json()

    async def inspect(self):
        async with self.api.client.get('/containers/%s/json' % self.Id) as r:
            if r.status != 200:
                raise status_error(r.status)
            return self.api.Container(await(r.json()))

    async def stop(self, timeout=None):
        async with self.api.client.post('/containers/%s/stop' % self.Id) as r:
            if r.status != 204:
                raise status_error(r.status)

    async def start(self):
        async with self.api.client.post('/containers/%s/start' % self.Id) as r:
            if r.status != 204:
                raise status_error(r.status)

    async def restart(self, timeout=None):
        async with self.api.client.post('/containers/%s/restart' % self.Id) as r:
            if r.status != 204:
                raise status_error(r.status)

    async def kill(self, signal=None):
        async with self.api.client.post('/containers/%s/kill' % self.Id) as r:
            if r.status != 204:
                raise status_error(r.status)

    @classmethod
    async def create(cls):
        pass

    def __hash__(self):
        return hash(self.Id)

    def __eq__(self, other):
        if isinstance(other, Container):
            return self.Id == other.Id
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Container):
            return self.Id != other.Id
        return NotImplemented

    def __repr__(self):
        return 'Container <%s>' % self.Id

    def __str__(self):
        return self.Id


class Containers(list, APIUnbound):

    @classmethod
    async def list(cls, filters=None, **labels):
        filters = filters or {}
        for label, val in labels.items():
            filters['label'] = filters.get('label', []) + [
                '%s=%s' % (label, val) if val else label
            ]

        # Build query
        q = {}
        if filters:
            q['filters'] = json.dump(filters)

        # Reduce to query string
        q = ('?%s' % '&'.join(
                '%s=%s' % (key, val) for key, val in filters.items()
            ) if q else '')

        async with cls.api.client.get('/containers/json%s' % q) as r:
            if r.status != 200:
                raise status_error(r.status)
            return cls.api.Containers([
                cls.api.Container(json)
                for json in
                await r.json()
            ])
