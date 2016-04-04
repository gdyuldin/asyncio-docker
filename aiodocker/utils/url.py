import json
from urllib.parse import quote


def build_url(*parts, **params):
    path = '/'.join(('',) + parts)
    return ''.join([path, query_string(**params)])


def query_string(**params):
    # Reduce to query string

    def parse(val):
        if not isinstance(val, (str, bytes)):
            val = json.dumps(val)
        return quote(val)

    return ('?%s' % '&'.join(
            '%s=%s' % (key, parse(val)) for key, val in params.items()
        ) if params else '')
