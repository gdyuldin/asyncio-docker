from asyncio_docker.registry import RegistryUnbound
from asyncio_docker.collections import DataMapping
from asyncio_docker.utils.url import build_url

from .errors import APIError, status_error

from jsonschema import validate, ValidationError
import json


PREFIX = 'images'


class Image(RegistryUnbound):

    def __init__(self, id, raw=None):
        self._id = id
        self._raw = raw

    @property
    def id(self):
        return self._id

    @property
    def data(self):
        return DataMapping(self._raw or {})

    async def inspect(self):
        req = self.client.get(build_url(PREFIX, self.id, 'json'))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)
            return DataMapping(await res.json())

    async def remove(self, no_prune=False, force=False):

        q = {
            'noprune': '1' if no_prune else '0',
            'force': '1' if force else '0'
        }

        req = self.client.delete(build_url(PREFIX, self.id, **q))
        async with req as res:
            if res.status != 200:
                raise await status_error(res)

    @classmethod
    async def build(cls, data, t, dockerfile=None, remote=None, q=False, nocache=False, pull=False, rm=True, forcerm=False, memory=None, memswap=None, cpushares=None, cpusetcpus=None, cpuperiod=None, cpuquota=None, buildargs=None, shmsize=None, labels=()):

        q = {'t': t, 'q': q, 'nocache': nocache, 'pull': pull, 'rm': rm, 'forcerm': forcerm}

        if dockerfile is not None:
            q['dockerfile'] = dockerfile
        if len(labels) > 0:
            q['labels'] = labels
        if remote is not None:
            q['remote'] = remote
        if memory is not None:
            q['memory'] = memory
        if memswap is not None:
            q['memswap'] = memswap
        if cpushares is not None:
            q['cpushares'] = cpushares
        if cpusetcpus is not None:
            q['cpusetcpus'] = cpusetcpus
        if cpuperiod is not None:
            q['cpuperiod'] = cpuperiod
        if cpuquota is not None:
            q['cpuquota'] = cpuquota
        if buildargs is not None:
            q['buildargs'] = buildargs
        if shmsize is not None:
            q['shmsize'] = shmsize

        req = cls.client.post(
            build_url('build', **q), data=data
        )
        async with req as res:
            if res.status != 200:
                raise await status_error(res)

            # Wait till full response is available
            data = (await res.text()).splitlines()
            if data:
                # Check last status, make sure it has no error
                last_status = json.loads(data[-1])
                if 'error' in last_status:
                    raise APIError(last_status['error'])

            images = await cls.list(filter=t)
            return images[0]

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
                # Check last status, make sure it has no error
                last_status = json.loads(data[-1])
                if 'error' in last_status:
                    raise APIError(last_status['error'])

            return cls(from_image)

    @classmethod
    async def list(cls, all=None, labels=None, dangling=False, filters=None,
            filter=None):

        f = {}
        for label, val in (labels or {}).items():
            f['label'] = f.get('label', []) + [
                '%s=%s' % (label, val) if val else label
            ]

        if dangling:
            f['dangling'] = ['true']

        filters = dict(f, **(filters or {}))
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
                cls(raw['Id'], raw=raw) for raw in await res.json()
            ]

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Image):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Image):
            return self.id != other.id
        return NotImplemented

    def __repr__(self):
        return 'Image <%s>' % self.id

    def __str__(self):
        return self.id
