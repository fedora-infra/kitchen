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
'''
----------
StrictDict
----------

:class:`kitchen.collections.StrictDict` provides a dictionary that treats
:class:`str` and :class:`unicode` as distinct key values.
'''

# Pylint disabled messages:
# :C0111: We're implementing the dict interface so just reference the dict
#   documentation rather than having our own docstrings

try:
    # :E0611: Pylint false positive.  We try to import from the stdlib but we
    #   have a fallback so this is okay.
    #pylint:disable-msg=E0611
    from collections import defaultdict
except ImportError:
    from kitchen.pycompat25.collections import defaultdict

class StrictDict(defaultdict):
    '''
    Map class that considers :class:`unicode` and :class:`str` different keys

    Ordinarily when you are dealing with a :class:`dict` keyed on strings you
    want to have keys that have the same characters end up in the same bucket
    even if one key is :class:`unicode` and the other is a byte :class:`str`.
    The normal :class:`dict` type does this for :term:`ASCII` characters (but
    not for anything outside of the :term:`ASCII` range.)

    Sometimes, however, you want to keep the two string classes strictly
    separate, for instance, if you're creating a single table that can map
    from :class:`unicode` characters to :class:`str` characters and vice
    versa.  This class will help you do that by making all :class:`unicode`
    keys evaluate to a different key than all :class:`str` keys.

    .. seealso::
        :class:`dict`
            for documentation on this class's methods.  This class implements
            all the standard :class:`dict` methods.  Its treatment of
            :class:`unicode` and :class:`str` keys as separate is the only
            difference.

    '''
    #pylint:disable-msg=C0111
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

__all__ = ('StrictDict',)
