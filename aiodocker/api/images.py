from aiodocker.api.registry import APIUnbound
from aiodocker.api.errors import APIError, status_error
from aiodocker.api.constants.schemas import CONFIG
from aiodocker.utils.schemas import schema_extract
from aiodocker.utils.convention import snake_case
from aiodocker.utils.url import build_url

from attrdict import AttrDict
from jsonschema import validate, ValidationError
import json


PREFIX = 'images'


class Image(APIUnbound):

    def __init__(self, name, raw=None):
        self._name = name
        self._raw = raw

    @property
    def data(self):
        return AttrDict(snake_case(self._raw or {}))

    @property
    def raw(self):
        return AttrDict(self._raw or {})

    async def inspect(self):
        return await self.api.Images.inspect(self.name)

    @property
    def name(self):
        return self._name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, Image):
            return self.name == other.name
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Image):
            return self.name != other.name
        return NotImplemented

    def __repr__(self):
        return 'Image <%s>' % self.name

    def __str__(self):
        return self.name


class Images(APIUnbound):

    @classmethod
    async def inspect(cls, name):
        req = cls.api.client.get(build_url(PREFIX, name, 'json'))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return AttrDict(**await(res.json()))

    @classmethod
    async def create(cls, from_image=None, from_src=None, repo=None,
            tag=None):

        if (from_image is None and from_src is None or from_image is not None
                and from_src is not None):
            raise ValueError("Specify either from_image or from_src")

        q = {}
        if from_image is not None:
            q['fromImage'] = from_image
        if from_src is not None:
            q['fromSrc'] = from_src
        if repo is not None:
            q['repo'] = repo
        if tag is not None:
            q['tag'] = tag

        req = cls.api.client.post(
            build_url(PREFIX, 'create', **q)
        )

        async with req as res:
            if res.status != 200:
                raise await status_error(res)

            # Wait till full response is available
            data = (await res.text()).splitlines()
            if data:
                # Check last status, make it has no error
                last_status = snake_case(json.loads(data[-1]))
                if 'error' in last_status:
                    raise APIError(last_status['error'])

    @classmethod
    async def list(cls, all=None, labels=None, filters=None, filter=None):
        filters = filters or {}
        for label, val in (labels or {}).items():
            filters['label'] = filters.get('label', []) + [
                '%s=%s' % (label, val) if val else label
            ]

        q = {}
        if filters:
            q['filters'] = filters

        if filter:
            q['filter'] = filter

        if all is not None:
            q['all'] = '1' if all else '0'

        req = cls.api.client.get(build_url(PREFIX, 'json', **q))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return [
                cls.api.Image(snake_case(raw)['name'], raw=raw) for raw in await res.json()
            ]
