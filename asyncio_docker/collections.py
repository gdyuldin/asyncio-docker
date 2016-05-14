import re
from collections import OrderedDict
from collections.abc import Mapping, Iterable
from itertools import chain


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


class DataMapping(Mapping):

    def __init__(self, items=None, **kwargs):
        if isinstance(items, Mapping):
            items = items.items()
        elif items is None:
            items = []

        self._mapping = {
            self._snake_case(key):  (key, val)
            for key, val in chain(items, kwargs.items())
        }


    @staticmethod
    def _snake_case(key):
        return all_cap_re.sub(r'\1_\2', first_cap_re.sub(r'\1_\2', key)).lower()

    @classmethod
    def _value(cls, val):
        if isinstance(val, Mapping):
            val = cls(val)
        elif isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
            val = type(val)([
                cls._value(item) for item in val
            ])
        return val

    def __getitem__(self, key):
        nkey = self._snake_case(key)
        if nkey in self._mapping:
            return self._value(self._mapping[nkey][1])
        raise KeyError(key)

    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError(name)

    def __iter__(self):
        return self.keys()

    def __len__(self):
        return len(self._mapping)

    def __contains__(self, key):
        return self._snake_case(key) in self._mapping

    def keys(self):
        for okey, val in self._mapping.values():
            yield okey

    def items(self):
        for okey, val in self._mapping.values():
            yield okey, self._value(val)

    def values(self):
        for okey, val in self._mapping.values():
            yield self._value(val)

    def get(self, key, default=None):
        if key in self:
            return self[key]
        return default

    @property
    def raw(self):
        return {
            val[0]: val[1]
            for val in self._mapping.values()
        }

    def __eq__(self, other):
        if isinstance(other, DataMapping):
            return self._mapping == other._mapping
        else:
            return self.raw == other

    def __ne__(self, other):
        if isinstance(other, DataMapping):
            return self._mapping != other._mapping
        else:
            return self.raw != other
