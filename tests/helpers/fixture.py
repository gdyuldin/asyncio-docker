import asyncio
from functools import wraps


def from_callable(fixture, *fixture_args, **fixture_kwargs):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            args += (fixture(*(args + fixture_args), **dict(kwargs, **fixture_kwargs)) or tuple())
            func(*args, **kwargs)
        return wrapper

    return decorator
