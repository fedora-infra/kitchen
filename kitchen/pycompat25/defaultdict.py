##
# Transcribed from http://code.activestate.com/recipes/523034/ on May 1, 2009
# by Jef Spaleta This code provides an emulation for the defaultdict
# functionality introduced in python 2.5's collection module
#
# Copyright (c) 2007 Justin Kirtland
# 
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
'''
-----------
defaultdict
-----------

This is a pure python implementation of defaultdict that is compatible with
the defaultdict class provided by python-2.5 and above.

.. seealso:: :class:`collections.defaultdict` for documentation on this module

'''
import types

from kitchen import _

try:
    # :W0611: We're importing the 2.5 version first.  If that doesn't work,
    # implement our own.
    # pylint: disable-msg=W0611
    from collections import defaultdict
except ImportError:
    defaultdict = None

class _defaultdict(dict):
    def __init__(self, default_factory=None, *args, **kwargs):
        if (default_factory is not None and
            not hasattr(default_factory, '__call__')):
            raise TypeError(_('First argument must be callable'))
        dict.__init__(self, *args, **kwargs)
        self.default_factory = default_factory

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = value = self.default_factory()
        return value

    def __reduce__(self):
        if self.default_factory is None:
            args = tuple()
        else:
            args = self.default_factory,
        return type(self), args, None, None, self.iteritems()

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return type(self)(self.default_factory, self)

    def __deepcopy__(self, memo):
        import copy
        return type(self)(self.default_factory,
                          copy.deepcopy(self.items()))
    def __repr__(self):
        # Note: Have to use "is not None"  otherwise we get an infinite
        # recursion
        if isinstance(self.default_factory, types.MethodType) \
                and self.default_factory.im_self is not None \
                and issubclass(self.default_factory.im_class, _defaultdict):
            defrepr = '<bound method sub._factory of defaultdict(...'
        else:
            defrepr = repr(self.default_factory)
        return 'defaultdict(%s, %s)' % (defrepr, dict.__repr__(self))

if not defaultdict:
    defaultdict = _defaultdict

__all__ = ('defaultdict',)
