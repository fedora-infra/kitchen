'''
The :mod:`kitchen.pycompat27` module contains implementations of functionality
introduced in python-2.7 for use on earlier versions of python.

.. versionchanged:: 0.2.3
    Made mswindows, MAXFD, and list2cmdline available from the module
'''
from kitchen.versioning import version_tuple_to_string

__version_info__ = ((1, 1, 0),)
__version__ = version_tuple_to_string(__version_info__)

__all__ = ('subprocess',)
