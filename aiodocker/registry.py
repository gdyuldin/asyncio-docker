import abc


class Registry(object):

    _types = []

    @classmethod
    def register(cls, typ):
        cls._types.append(typ)

    def __init__(self, client):
        self.client = client
        for typ in self._types:
            setattr(self, typ.__name__, typ.factory(self))


class RegistryBound(object):
    pass


class RegistryUnboundMeta(abc.ABCMeta):

    # Inherit from ABCMeta in order to avoid conflicts with AttrDict
    def __new__(mcls, name, bases, namespace):
        cls = super(RegistryUnboundMeta, mcls).__new__(mcls, name, bases, namespace)

        if bases == (object,):
            return cls

        if RegistryBound not in bases:
            Registry.register(cls)

        return cls


class RegistryUnboundError(Exception):
    pass


class RegistryUnbound(object, metaclass=RegistryUnboundMeta):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'registry'):
            raise RegistryUnboundError()
        return object.__new__(cls)

    @classmethod
    def factory(cls, registry):
        return type(cls.__name__, (cls, RegistryBound), {
            'registry': registry,
            'client': registry.client
        })
