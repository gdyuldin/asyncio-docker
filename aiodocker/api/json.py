class JSONBaseObject(object):

    def _parse(self, value):
        if isinstance(value, dict):
            return self.get_object(value)
        if isinstance(value, list):
            value = [
                self._parse(item)
                for item in value
            ]
        return value

    def get_json(self):
        raise NotImplementedError()

    def get_object(json):
        raise NotImplementedError()

    def __getitem__(self, key):
        json = self.get_json()
        if key in json:
            return self._parse(json[key])
        raise KeyError(key)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __repr__(self):
        return repr(self.get_json())


class JSONRoot(JSONBaseObject):

    def get_object(self, json):
        return JSONObject(json)


class JSONObject(JSONBaseObject):

    def get_object(self, json):
        return JSONObject(json)

    def __init__(self, json):
        self._json = json

    def get_json(self):
        return self._json
