# -*- coding: utf-8 -*-
#
# Copyright (c) 2010 Red Hat, Inc
#
# This file is part of kitchen.core
# 
# kitchen.core is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# kitchen.core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with python-fedora; if not, see <http://www.gnu.org/licenses/>
#
# Authors:
#   Toshio Kuratomi <toshio@fedoraproject.org>

'''
Importing this module makes sure that a set and frozenset type have been defined
'''
import __builtin__
if not hasattr(__builtin__, 'set'):
    import sets
    __builtin__.set = sets.Set
    
if not hasattr(__builtin__, 'frozenset'):
    import sets
    __builtin__.frozenset = sets.ImmutableSet
