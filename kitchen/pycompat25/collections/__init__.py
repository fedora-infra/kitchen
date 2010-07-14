try:
    from collections import defaultdict
except ImportError:
    from _defaultdict import defaultdict

__all__ = ('defaultdict',)
