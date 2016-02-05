from functools import reduce

def schema_extract(mapping, schema):
    # Filter out any key not present in schema
    mapping = {
        key: val for
        key, val in mapping.items()
        if key in schema['properties']
    }

    def omit_null(out, keyval):
        key, val = keyval
        typ = schema['properties'][key]['type']
        if val is None and typ != 'null' and 'null' not in typ:
            return out

        out[key] = val
        return out

    # Filter out None values
    mapping = reduce(omit_null, mapping.items(), {})

    return mapping
