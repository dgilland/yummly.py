"""Main package API entry point.

Core objects imported here.
"""

from client import Client, YummlyError, Timeout

from .__meta__ import (
    __title__,
    __summary__,
    __url__,
    __version__,
    __author__,
    __email__,
    __license__
)

__all__ = ['Client', 'YummlyError', 'Timeout']
