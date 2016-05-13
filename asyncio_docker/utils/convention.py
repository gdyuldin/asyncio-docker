import re


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def snake_case(val):
    if isinstance(val, str):
        return all_cap_re.sub(r'\1_\2', first_cap_re.sub(r'\1_\2', val)).lower()
    elif isinstance(val, (list, set, tuple)):
        return type(val)(
            snake_case(v)
            for v in val
        )
    elif isinstance(val, dict):
        return {
            snake_case(k): snake_case(v) for
            k, v in val.items()
        }

    return val
