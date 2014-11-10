try:
    #:E0611: deafultdict doesn't exist in python-2.4 or less but that's why we
    #   have it in a try: except:.  So we can use our version if necessary.
    #pylint:disable-msg=E0611
    from collections import defaultdict
except ImportError:
    from kitchen.pycompat25.collections._defaultdict import defaultdict

__all__ = ('defaultdict',)
