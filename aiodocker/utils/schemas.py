from pydash.collections import reduce_
from pydash.objects import pick


def schema_extract(mapping, schema):
    # Filter out any key not present in schema
    mapping = pick(mapping, list(schema['properties'].keys()))

    def omit_null(out, val, key):
        typ = schema['properties'][key]['type']
        if val is None and typ != 'null' and 'null' not in typ:
            return out

        out[key] = val
        return out

    # Filter out None values
    mapping = reduce_(mapping, omit_null, {})

    return mapping
