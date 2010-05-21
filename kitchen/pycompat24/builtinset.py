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
Importing this module makes sure that a set and frozenset type have been defined
'''
import __builtin__

def add_builtin_set():
    '''If there's no set builtin, add the implementations from the sets module

    This function makes sure that a set and frozenset type are available in
    the __builtin__ namespace.  It does not overwrite any set or frozenset
    that is already present so it's safe to use this as boilerplate in code
    that needs to remain python-2.3 compatible but may also run on python-2.4+
    '''
    if not hasattr(__builtin__, 'set'):
        import sets
        __builtin__.set = sets.Set

    if not hasattr(__builtin__, 'frozenset'):
        import sets
        __builtin__.frozenset = sets.ImmutableSet

__all__ = (add_builtin_set,)
