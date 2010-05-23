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
In python-2.4, a builtin set type was added to python.  This module provides
a function to emulate that on python-2.3 by using the :mod:`sets` module.
'''
import __builtin__

def add_builtin_set():
    '''If there's no set builtin, add the implementations from the sets module

    This function makes sure that a set and frozenset type are available in
    the __builtin__ namespace.  Since the function checks whether set and
    frozenset are already present in the :mod:`__builtin__` namespace and
    refuses to overwrite those if found, it's safe to call this in multiple
    places and in scripts run under python-2.4+, where a more efficient set
    implementation is already present in the :mod:`__builtin__` namespace.

    However, since this function modifies __builtin__ there's no need to call
    it more than once  so you likely want to do something like this when your
    program loads::

        myprogram/__init__.py:

        from kitchen.pycompat24 import builtinset
        builtinset.add_builtin_set()

    Then you can use set() and frosenset anywhere in your code::

        myprogram/compute.py:

        def math_students(algebra_student_list, geometry_student_list):
            return set(algebra_student_list) union set(geometry_student_list)
    '''
    if not hasattr(__builtin__, 'set'):
        import sets
        __builtin__.set = sets.Set

    if not hasattr(__builtin__, 'frozenset'):
        import sets
        __builtin__.frozenset = sets.ImmutableSet

__all__ = (add_builtin_set,)
