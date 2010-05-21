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

__version_info__ = ((0, 1),)

import itertools

def version_tuple_to_string(version_info):
    '''Return a PEP-386 version string from a PEP-386 style version tuple

    This function implements just enough of PEP-386 to satisfy our needs.
    PEP-386 defines a standard format for version strings and refers to
    a function that will be merged into the stdlib that transforms a tuple of
    version information into a standard version string.  This function is an
    implementation of that function.  Once that function becomes available we
    will dep on it and deprecate this function.

    __version_info__ takes the form that NormalizedVersion.from_parts() uses::

        ((Major, Minor, [Micros]), [(Alpha/Beta/rc marker, version)],
            [(post/dev marker, version)])

        Ex: ((1, 0, 0), ('a', 2), ('dev', 3456))

    It generates a PEP-386 compliant version string::

        N.N[.N]+[{a|b|c|rc}N[.N]+][.postN][.devN]

        Ex: 1.0.0a2.dev3456

    Note that this function does next to no error checking.  It's up to the
    person defining the version tuple to make sure that the values make sense.
    If the PEP-386 compliant version parser doesn't get released soon we'll
    look at making this a better function.
    '''
    v = []
    for values in version_info:
        if isinstance(values[0], int):
            v.append('.'.join(itertools.imap(str, values)))
        elif values[0] in ('a', 'b', 'c', 'rc'):
            v.append('%s%s' %
                    (values[0], '.'.join(itertools.imap(str, values[1:])) or str(0)))
        else:
            v.append('.%s%s' % (values[0], values[1]))
    return ''.join(v)

__version__ = version_tuple_to_string(__version_info__)

__all__ = ('version_tuple_to_string',)
