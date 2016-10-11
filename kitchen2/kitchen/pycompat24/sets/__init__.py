# -*- coding: utf-8 -*-
#
# Copyright (c) 2010 Red Hat, Inc
#
# This file is part of kitchen
#
# kitchen is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# kitchen is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for
# more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with kitchen; if not, see <http://www.gnu.org/licenses/>
#
# Authors:
#   Toshio Kuratomi <toshio@fedoraproject.org>

'''
In python-2.4, a builtin :class:`set` type was added to python.  This module
provides a function to emulate that on python-2.3 by using the :mod:`sets`
module.

:func:`set`
    Create a set.  If running on python 2.4+ this is the :class:`set`
    constructor.  If using python-2.3, it's :class:`sets.Set`.

:func:`frozenset`
    Create a frozenset.  If running on python2.4+ this is the
    :class:`frozenset` constructor.  If using python-2.3, it's
    :class:`sets.ImmutableSet`.

.. versionchanged:: 0.2.0 API: kitchen.pycompat24 1.0.0
    Added set and frozenset
'''
import __builtin__

# Setup set and frozenset on this module
# :W0622,C0103: The purpose of this module is to define set and frozenset if
#   they aren't in builtins already so we disregard these pylint warnings
#pylint:disable-msg=W0622,C0103
if not hasattr(__builtin__, 'set'):
    import sets
    set = sets.Set
else:
    set = set

if not hasattr(__builtin__, 'frozenset'):
    import sets
    frozenset = sets.ImmutableSet
else:
    frozenset = frozenset
#pylint:enable-msg=W0622,C0103

def add_builtin_set():
    '''If there's no set builtin, us the :mod:`sets` module to make one

    This function makes sure that a :class:`set` and :class:`frozenset` type
    are available in the :mod:`__builtin__` namespace.  Since the function
    checks whether :class:`set` and :class:`frozenset` are already present in
    the :mod:`__builtin__` namespace and refuses to overwrite those if found,
    it's safe to call this in multiple places and in scripts run under
    python-2.4+, where a more efficient set implementation is already present
    in the :mod:`__builtin__` namespace.

    However, since this function modifies :mod:`__builtin__` there's no need
    to call it more than once  so you likely want to do something like this
    when your program loads::

        myprogram/__init__.py:

        from kitchen.pycompat24 import sets
        builtinset.add_builtin_set()

    You can then use :func:`set` and :func:`frozenset` anywhere in your code::

        myprogram/compute.py:

        def math_students(algebra_student_list, geometry_student_list):
            return set(algebra_student_list) union set(geometry_student_list)
    '''
    if not hasattr(__builtin__, 'set'):
        __builtin__.set = set

    if not hasattr(__builtin__, 'frozenset'):
        __builtin__.frozenset = frozenset

__all__ = ('add_builtin_set', 'set', 'frozenset')
