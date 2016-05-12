import asyncio
from functools import wraps


def run_until_complete(timeout=None):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            loop = asyncio.get_event_loop()
            loop.run_until_complete(func(self, *args, **kwargs))
        return wrapper

    return decorator
