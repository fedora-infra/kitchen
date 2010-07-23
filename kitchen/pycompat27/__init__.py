import sys

from kitchen.versioning import version_tuple_to_string

__version_info__ = ((1, 0, 0),)
__version__ = version_tuple_to_string(__version_info__)

if sys.version_info >= (2, 7):
    import subprocess as subprocess
else:
    import _subprocess as subprocess

__all__ = ('subprocess',)
