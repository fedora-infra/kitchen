##
# Transcribed from http://code.activestate.com/recipes/523034/ on May 1, 2009
# by Jef Spaleta This code provides an emulation for the defaultdict
# functionality introduced in python 2.5's collection module
#
# Changes from the original:
# * Change the return value from __reduce__ to use iteritems() to prevent
#   a segfault when pickling. (Jef Spaleta)
# * Change how we setup the module to use collections.defaultdict by default
#   (Toshio Kuratomi)
#
# Copyright (c) 2007 Justin Kirtland
#
# PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
# --------------------------------------------
#
# 1. This LICENSE AGREEMENT is between the Python Software Foundation ("PSF"),
#    and the Individual or Organization ("Licensee") accessing and otherwise
#    using this software ("Python") in source or binary form and its
#    associated documentation.
#
# 2. Subject to the terms and conditions of this License Agreement, PSF hereby
#    grants Licensee a nonexclusive, royalty-free, world-wide license to
#    reproduce, analyze, test, perform and/or display publicly, prepare
#    derivative works, distribute, and otherwise use Python alone or in any
#    derivative version, provided, however, that PSF's License Agreement and
#    PSF's notice of copyright, i.e., "Copyright (c) 2001, 2002, 2003, 2004,
#    2005, 2006 Python Software Foundation; All Rights Reserved" are retained
#    in Python alone or in any derivative version prepared by Licensee.
#
# 3. In the event Licensee prepares a derivative work that is based on or
#    incorporates Python or any part thereof, and wants to make the derivative
#    work available to others as provided herein, then Licensee hereby agrees
#    to include in any such work a brief summary of the changes made to
#    Python.
#
# 4. PSF is making Python available to Licensee on an "AS IS" basis.  PSF
#    MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR IMPLIED.  BY WAY OF
#    EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND DISCLAIMS ANY
#    REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR FITNESS FOR ANY
#    PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT INFRINGE ANY THIRD
#    PARTY RIGHTS.
#
# 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON FOR ANY
#    INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS AS A RESULT OF
#    MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON, OR ANY DERIVATIVE
#    THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF.
#
# 6. This License Agreement will automatically terminate upon a material
#    breach of its terms and conditions.
#
# 7. Nothing in this License Agreement shall be deemed to create any
#    relationship of agency, partnership, or joint venture between PSF and
#    Licensee.  This License Agreement does not grant permission to use PSF
#    trademarks or trade name in a trademark sense to endorse or promote
#    products or services of Licensee, or any third party.
#
# 8. By copying, installing or otherwise using Python, Licensee agrees to be
#    bound by the terms and conditions of this License Agreement.

'''
-----------
defaultdict
-----------

This is a pure python implementation of defaultdict that is compatible with
the defaultdict class provided by python-2.5 and above.

.. seealso::
    :class:`collections.defaultdict`
        for documentation on this module
'''

# Pylint disabled messages
#
# :C0103: We're defnining a compatible class name therefore we need to match
#   the format of that name.

import types

# :C0103, W0613: We're implementing the python-2.5 defaultdict API so
#   we have to use the same names as python.
# :C0111: We point people at the stdlib API docs for defaultdict rather than
#   reproduce it here.
#pylint:disable-msg=C0103,W0613,C0111

class defaultdict(dict):
    def __init__(self, default_factory=None, *args, **kwargs):
        if (default_factory is not None and
                not hasattr(default_factory, '__call__')):
            raise TypeError('First argument must be callable')
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
                and issubclass(self.default_factory.im_class, defaultdict):
            defrepr = '<bound method sub._factory of defaultdict(...'
        else:
            defrepr = repr(self.default_factory)
        return 'defaultdict(%s, %s)' % (defrepr, dict.__repr__(self))

__all__ = ('defaultdict',)
