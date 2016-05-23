import asyncio
from functools import wraps


def run_until_complete(timeout=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(asyncio.wait_for(func(*args, **kwargs), timeout))
        return wrapper

    return decorator
