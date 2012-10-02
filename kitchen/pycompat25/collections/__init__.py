# All versions of python3 include defaultdict.  This module just exists for
# backwards compatibility
#
import warnings

warnings.warn('In python3, kitchen.pycompat25.collections.defaultdict is'
        ' deprecated.  If you do not need to maintain compatibility with'
        ' python less than 2.5 use collections.defaultdict from the stdlib'
        ' instead.',
        PendingDeprecationWarning, stacklevel=2)

#:E0611: deafultdict doesn't exist in python-2.4 or less but that's why we
#   have it in a try: except:.  So we can use our version if necessary.
#pylint:disable-msg=E0611
from collections import defaultdict

__all__ = ('defaultdict',)
