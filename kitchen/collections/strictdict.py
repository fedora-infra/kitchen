# -*- coding: utf-8 -*-
#
# Copyright (c) 2010 Red Hat, Inc
#
# kitchen is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# kitchen is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with kitchen; if not, see <http://www.gnu.org/licenses/>
#
# Authors:
#   Toshio Kuratomi <toshio@fedoraproject.org>
try:
    from collections import defaultdict
except ImportError:
    from kitchen.pycompat25.defaultdict import defaultdict

class StrictDict(defaultdict):
    '''
    Mapping class that considers unicode and str different keys

    Ordinarily when you are dealing with data you want to have keys that have
    the same characters end up in the same bucket even if one key is
    :class:`unicode` and the other is a byte :class:`str`.  If you cannot do
    that, then this class will help you by making all :class:`unicode` strings
    evaluate to a different key than all :class:`str` keys.
    '''
    def __getitem__(self, key):
        return defaultdict.__getitem__(self, (repr(key), key))

    def __setitem__(self, key, value):
        defaultdict.__setitem__(self, (repr(key), key), value)

    def __delitem__(self, key):
        defaultdict.__delitem__(self, (repr(key), key))

    def __iter__(self):
        for i in defaultdict.__iter__(self):
            yield i[1]

    iterkeys = __iter__

    def keys(self):
        return list(self.__iter__())

    def __contains__(self, key):
        return defaultdict.__contains__(self, (repr(key), key))
