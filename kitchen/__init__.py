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
# License along with python-fedora; if not, see <http://www.gnu.org/licenses/>
#
# Authors:
#   Toshio Kuratomi <toshio@fedoraproject.org>
#
'''
Kitchen

Aggregate of a bunch of unrelated but helpful python modules.
'''
from kitchen import i18n

(_, P_) = i18n.easy_gettext_setup('kitchen.core')

__version_info__ = ((0, 1), ('a', 1))
# just enough of PEP-386 to satisfy our needs
# Here's the PEP386 format::
#   N.N[.N]+[{a|b|c|rc}N[.N]+][.postN][.devN]
#
# __version_info__ takes the form that NormalizedVersion.from_parts() uses::
# ((Major, Minor, [Micros]), [(Alpha/beta/rc marker, version)], [(post/dev marker, version)]
#
# We do even less error checking than the current PEP-386 imlementation
# because we have control over __version_info__.  When PEP-386 is available
# we'll use it by default.
v = []
for values in __version_info__:
    if isinstance(values[0], int):
        v.append('.'.join(str(x) for x in values))
    elif values[0] in ('a', 'b', 'c', 'rc'):
        v.append('%s%s' %
                (values[0], '.'.join(str(x) for x in values[1:]) or str(0)))
    else:
        v.append('.%s%s' % (values[0], values[1]))
__version__ = ''.join(v)

__all__ = tuple()
