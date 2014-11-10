'''
The :mod:`kitchen.pycompat25` module contains implementations of functionality
introduced in python-2.5.
'''

from kitchen.versioning import version_tuple_to_string

__version_info__ = ((1, 0, 0),)
__version__ = version_tuple_to_string(__version_info__)


__all__ = ('collections',)
