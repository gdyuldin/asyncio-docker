import json
from urllib.parse import quote

def query_string(**params):
    # Reduce to query string

    def parse(val):
        if isinstance(val, (dict, list, set, tuple)):
            val = json.dumps(val)
        return quote(val)

    return ('?%s' % '&'.join(
            '%s=%s' % (key, parse(val)) for key, val in params.items()
        ) if params else '')
