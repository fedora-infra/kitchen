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
#
'''
Kitchen

Aggregate of a bunch of unrelated but helpful python modules.
'''
from kitchen import i18n
from kitchen import versioning

(_, P_) = i18n.easy_gettext_setup('kitchen.core')

__version_info__ = ((0, 1), ('a', 2))
__version__ = versioning.version_tuple_to_string(__version_info__)

__all__ = tuple()
