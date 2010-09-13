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
Implement the modern base64 interface.  Note that this only implements the
base64 functions.  Specifically, it does not implement b32encode, b32decode,
b16encode, or b16decode.
'''
import sys

if sys.version_info >= (2, 4):
    from base64 import *
else:
    from _base64 import *

__all__ = ( 'b64decode', 'b64encode', 'standard_b64decode',
        'standard_b64encode', 'urlsafe_b64decode', 'urlsafe_b64encode',)
