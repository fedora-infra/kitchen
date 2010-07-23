from kitchen.versioning import version_tuple_to_string

__version_info__ = ((1, 1, 0),)
__version__ = version_tuple_to_string(__version_info__)

import strictdict
from strictdict import StrictDict

__all__ = ('strictdict', 'StrictDict',)
