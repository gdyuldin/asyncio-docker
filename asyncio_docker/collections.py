import re
from collections import OrderedDict
from collections.abc import Mapping, Iterable
from itertools import chain


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


class DataMapping(Mapping):

    def __init__(self, items=None, **kwargs):
        self._mapping = OrderedDict()
        if isinstance(items, Mapping):
            items = items.items()
        elif items is None:
            items = []

        for key, val in chain(items, kwargs.items()):
            self._mapping[_snake_case(key)] = (key, val)

    @staticmethod
    def _snake_case(key):
        return all_cap_re.sub(r'\1_\2', first_cap_re.sub(r'\1_\2', key)).lower()

    @classmethod
    def _parse(cls, val):
        return val

    def __getitem__(self, key):
        nkey = DataMapping._snake_case(key)
        if nkey in self._mapping:
            return DataMapping._parse(self._mapping[nkey][1])
        raise KeyError(key)

    def __iter__(self):
        return self.keys()

    def __len__(self):
        return len(self._mapping)

    def __contains__(self, key):
        return DataMapping._snake_case(key) in self._mapping

    def keys(self):
        for okey, val in self._mapping.values():
            yield okey

    def items(self):
        for okey, val in self._mapping.values():
            yield okey, DataMapping._parse(val)

    def values():
        for okey, val in self._mapping.values():
            yield DataMapping._parse(val)

    def get(self, key):
        pass

    def __eq__(self, other):
        pass

    def __ne__(self, other):
        pass
