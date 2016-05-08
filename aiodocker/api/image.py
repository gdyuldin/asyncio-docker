from aiodocker.registry import RegistryUnbound
from aiodocker.api.errors import APIError, status_error
from aiodocker.utils.convention import snake_case
from aiodocker.utils.url import build_url

from attrdict import AttrDict
from jsonschema import validate, ValidationError
import json


PREFIX = 'images'


class Image(RegistryUnbound):

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
        req = self.client.get(build_url(PREFIX, self.name, 'json'))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return AttrDict(**await(res.json()))

    async def remove(self, no_prune=False, force=False):

        q = {
            'noprune': '1' if no_prune else '0',
            'force': '1' if force else '0'
        }

        req = self.client.delete(build_url(PREFIX, self.name, **q))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)

    @classmethod
    async def create(cls, from_image=None, from_src=None, repo=None, tag=None):

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

        req = cls.client.post(
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

            return cls(from_image)

    @classmethod
    async def list(cls, all=None, labels=None, dangling=False, filters=None,
            filter=None):

        filters = filters or {}

        for label, val in (labels or {}).items():
            filters['label'] = filters.get('label', []) + [
                '%s=%s' % (label, val) if val else label
            ]

        if dangling:
            filters['dangling'] = ['true']

        q = {}
        if filters:
            q['filters'] = filters

        if filter:
            q['filter'] = filter

        if all is not None:
            q['all'] = '1' if all else '0'

        req = cls.client.get(build_url(PREFIX, 'json', **q))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return [
                cls(snake_case(raw)['id'], raw=raw) for raw in await res.json()
            ]

    @property
    def name(self):
        return self._name

    @property
    def is_dangling(self):
        if 'repo_tags' in self.data:
            return '<none>:<none>' in self.data.repo_tags
        return False

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
