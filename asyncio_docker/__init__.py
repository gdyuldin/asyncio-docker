from .utils.version import get_version

API_VERSION = (1, 24)
VERSION = API_VERSION + (0, 'beta', 7)

__version__ = get_version(VERSION)
