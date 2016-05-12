import asyncio
import logging
from functools import wraps

from nose2.events import Plugin


logger = logging.getLogger('nose2.plugins.asycnio')


class AsyncioPlugin(Plugin):
    configSection = 'asyncio'
    alwaysOn = True

    def startTestRun(self, event):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

    def stopTestRun(self, event):
        self._loop.close()


def run_until_complete(timeout=None):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            loop = asyncio.get_event_loop()
            loop.run_until_complete(func(self, *args, **kwargs))
        return wrapper

    return decorator
