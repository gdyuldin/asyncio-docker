import __main__

from .utils.version import get_version

VERSION = (0, 1, 0, 'alpha', 0)

__version__ = get_version(VERSION)


# Do not import any more internals if setup.py
# is running this.
if not getattr(__main__, '_is_setup', False):
    pass
