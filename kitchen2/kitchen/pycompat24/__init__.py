'''
The :mod:`kitchen.pycompat24` module contains implementations of functionality
introduced in python-2.4 for use on earlier versions of python.
'''
from kitchen.versioning import version_tuple_to_string

__version_info__ = ((1, 1, 0),)
__version__ = version_tuple_to_string(__version_info__)

__all__ = ('base64', 'sets', 'subprocess')
