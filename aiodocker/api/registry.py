class APIRegistry(object):

    _types = []

    @classmethod
    def register(cls, typ):
        cls._types.append(typ)

    def __init__(self, client):
        self.client = client
        for typ in self._types:
            setattr(self, typ.__name__, typ.factory(self))


class APIBound(object):
    pass


class APIUnboundMeta(type):

    def __new__(mcls, name, bases, namespace):
        cls = super(APIUnboundMeta, mcls).__new__(mcls, name, bases, namespace)

        if bases == (object,):
            return cls

        if APIBound not in bases:
            APIRegistry.register(cls)

        return cls


class APIUnboundError(Exception):
    pass


class APIUnbound(object, metaclass=APIUnboundMeta):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'api'):
            raise APIUnboundError()
        return object.__new__(cls)

    @classmethod
    def factory(cls, api):
        return type(cls.__name__, (cls, APIBound), {
            'api': api
        })
