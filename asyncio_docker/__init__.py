from .utils.version import get_version

API_VERSION = (1, 23)
VERSION = API_VERSION + (0, 'beta', 2)

__version__ = get_version(VERSION)
