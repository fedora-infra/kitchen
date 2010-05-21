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
import base64

def _b64encode(s, altchars=None):
    '''Compatibility function for python-2.4's base64.b64encode

    .. seealso:: http://docs.python.org/library/base64.html
    '''
    s = base64.encodestring(s)
    if altchars:
        for chars in zip(('+','/'), altchars):
            s = s.replace(chars[0], chars[1])
    return ''.join(s.split())

def _b64decode(s, altchars=None):
    '''Compatibility function for python-2.4's base64.b64decode

    .. seealso:: http://docs.python.org/library/base64.html
    '''
    if altchars:
        for chars in zip(altchars, ('+', '/')):
            s = s.replace(chars[0], chars[1])
    s = base64.decodestring(s)
    return s

def _standard_b64encode(s):
    '''Compatibility function for python-2.4's base64.standard_b64encode

    .. seealso:: http://docs.python.org/library/base64.html
    '''
    return b64encode(s)

def _standard_b64decode(s):
    '''Compatibility function for python-2.4's base64.standard_b64decode

    .. seealso:: http://docs.python.org/library/base64.html
    '''
    return b64decode(s)

def _urlsafe_b64encode(s):
    '''Compatibility function for python-2.4's base64.urlsafe_b64encode

    .. seealso:: http://docs.python.org/library/base64.html
    '''
    return b64encode(s, altchars='-_')

def _urlsafe_b64decode(s):
    '''Compatibility function for python-2.4's base64.urlsafe_b64decode

    .. seealso:: http://docs.python.org/library/base64.html
    '''
    return b64decode(s, altchars='-_')

if hasattr(base64, 'b64encode'):
    b64encode = base64.b64encode
else:
    b64encode = _b64encode

if hasattr(base64, 'b64decode'):
    b64decode = base64.b64decode
else:
    b64decode = _b64decode

if hasattr(base64, 'standard_b64encode'):
    standard_b64encode = base64.standard_b64encode
else:
    standard_b64encode = _standard_b64encode

if hasattr(base64, 'standard_b64decode'):
    standard_b64decode = base64.standard_b64decode
else:
    standard_b64decode = _standard_b64decode

if hasattr(base64, 'urlsafe_b64encode'):
    urlsafe_b64encode = base64.urlsafe_b64encode
else:
    urlsafe_b64encode = _urlsafe_b64encode

if hasattr(base64, 'urlsafe_b64decode'):
    urlsafe_b64decode = base64.urlsafe_b64decode
else:
    urlsafe_b64decode = _urlsafe_b64decode

__all__ = ( 'b64decode', 'b64encode', 'standard_b64decode',
        'standard_b64encode', 'urlsafe_b64decode', 'urlsafe_b64encode',)
