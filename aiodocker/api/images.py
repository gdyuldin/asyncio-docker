from aiodocker.api.registry import APIUnbound
from aiodocker.api.errors import status_error
from aiodocker.api.constants.schemas import CONFIG
from aiodocker.utils.schemas import schema_extract
from aiodocker.utils.url import build_url

import json
from jsonschema import validate, ValidationError


PREFIX = 'images'


class Image(APIUnbound):

    def __init__(self, name):
        self._name = name

    def inspect(self):
        return self.api.Images.inspect(self.Name)

    @property
    def Name(self):
        return self._name

    def __hash__(self):
        return hash(self.Name)

    def __eq__(self, other):
        if isinstance(other, Image):
            return self.Name == other.Name
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Image):
            return self.Name != other.Name
        return NotImplemented

    def __repr__(self):
        return 'Image <%s>' % self.Name

    def __str__(self):
        return self.Name


class Images(APIUnbound):

    @classmethod
    async def inspect(cls, name):
        req = self.api.client.get(build_url(PREFIX, name, 'json'))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return self.api.Image(**await(res.json()))

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

        req = cls.api.client.get(build_url(PREFIX, 'json', **q))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return [
                cls.api.Image(val['Name']) for val in await res.json()
            ]
