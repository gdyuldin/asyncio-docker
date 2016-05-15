import re
from collections.abc import Mapping, Iterable


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


class DataMapping(dict):

    def __init__(self, *args, **kwargs):
        super(DataMapping, self).__init__(*args, **kwargs)
        self._map = {
            self._snake_case(key):  key
            for key in self.keys()
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

    def __hasattr__(self, name):
        return self._snake_case(name) in self._map

    def __getattr__(self, name):
        nkey = self._snake_case(name)
        if nkey in self._map:
            return self._value(self[self._map[nkey]])
        raise AttributeError(name)
