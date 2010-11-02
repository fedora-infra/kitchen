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
Implement the modern base64 interface.

Python-2.4 and above have a new API for the base64 module.  This is a backport
of that module for use on python-2.3.

.. seealso::
    :mod:`base64`
        for information about using the functions provided here.
'''
import sys

# :W0401,W0614: The purpose of this module is to create a backport of base64
# so we ignore these pylint warnings
#pylint:disable-msg=W0401,W0614
if sys.version_info >= (2, 4):
    from base64 import *
else:
    from kitchen.pycompat24.base64._base64 import *

__all__ = ( 'b16decode', 'b16encode', 'b32decode', 'b32encode', 'b64decode',
        'b64encode', 'decode', 'decodestring', 'encode', 'encodestring',
        'standard_b64decode', 'standard_b64encode', 'urlsafe_b64decode',
        'urlsafe_b64encode',)
