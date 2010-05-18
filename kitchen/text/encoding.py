# -*- coding: utf-8 -*-
#
# Copyright (c) 2010 Red Hat, Inc.
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
#   Seth Vidal
#
# Portions of code taken from yum/i18n.py and
# python-fedora: fedora/textutils.py

'''
Utility functions to handle conversion of byte strings and unicode strings.
'''
import warnings

from kitchen import _

try:
    import chardet
except ImportError:
    chardet = None

# Define a threshold for chardet confidence.  If we fall below this we decode
# byte strings we're guessing about as latin1
_chardet_threshhold = 0.6

def guess_encoding(byte_string, disable_chardet=False):
    '''Try to guess the encoding of a byte_string

    :arg byte_string: byte_string to guess the encoding of
    :kwarg disable_chardet: If this is True, we never attempt to use
        :mod:`chardet` to guess the encoding.  This is useful if you need to
        have reproducability whether chardet is installed or not.  Default:
        False.
    :raises ValueError: if byte_string is not a byte string (str) type
    :returns: string containing a guess at the encoding of byte_string

    We start by attempting to decode the bytes as utf8.  If this succeeds we
    tell the world it's utf8 text.  If it doesn't and :mod:`chardet` is
    installed on the system and :attr:`disable_chardet` is False this function
    will use it to try detecting the encoding of the byte_string.  If it is
    not installed or chardet cannot determine the encoding with a high enough
    confidence then we rather arbitrarily claim that it is latin1.  Since latin1
    will encode to every byte, decoding from laint1 to unicode will not cause
    UnicodeErrors even if the output is mangled.
    '''
    if not isinstance(byte_string, str):
        raise ValueError(_('byte_string must be a byte string (str)'))
    input_encoding = 'utf8'
    try:
        unicode(byte_string, input_encoding, 'strict')
    except UnicodeDecodeError:
        input_encoding = None

    if not input_encoding and chardet and not disable_chardet:
        detection_info = chardet.detect(byte_string)
        if detection_info['confidence'] >= _chardet_threshhold:
            input_encoding = detection_info['encoding']

    if not input_encoding:
        input_encoding = 'latin1'

    return input_encoding

def to_unicode(obj, encoding='utf8', errors='replace', non_string='empty'):
    '''Convert an object into a unicode string

    Usually, this should be used on a byte string but it can take byte strings
    and unicode strings intelligently.  non_string objects are handled in
    different ways depending on the setting of the non_string parameter.

    The default values of this function are set so as to always return
    a unicode string and never raise an error when converting from bytes to
    unicode.  However, when you do not pass validly encoded text as the byte
    string (or a non-string object), you may end up with output that you don't
    expect.  Be sure you understand the requirements of your data, not just
    ignore errors by passing it through this function.

    :arg obj: Object to convert to a unicode string.  This should normally be
        a byte string
    :kwarg encoding: What encoding to try converting the byte string as.
        Defaults to utf8
    :kwarg errors: If errors are given, perform this action.  Defaults to
        'replace' which replaces the error with a character that means the bytes
        were unable to be decoded.  Other values are those that can be given to
        the unicode constructor, for instance 'strict' which raises an
        exception and 'ignore' which simply omits the non-decodable
        characters.
    :kwargs non_string: How to treat non_string values.  Possible values are:
            :empty: Return an empty string
            :strict: Raise a TypeError
            :passthru: Return the object unchanged
            :simplerepr: Attempt to call the object's "simple representation"
                method and return that value.  Python-2.3+ has two methods
                that try to return a simple representation: __unicode__() and
                __str__().  We first try to get a usable value from
                __unicode__().  If that fails we try the same with __str__().
            :repr: Attempt to return a unicode string of the repr of the
                object
        The Default is 'empty'
    :raises TypeError: if :attr:`non_string` is 'strict' and a non-basestring
        object is passed in or if :attr:`non_string` is set to an unknown value
    :raises UnicodeDecodeError: if :attr:`errors` is 'strict' and the obj is
        not decodable using the given encoding
    :returns: unicode string or the original object depending on the value of
        non_string.
    '''
    if isinstance(obj, basestring):
        if isinstance(obj, unicode):
            return obj
        return unicode(obj, encoding=encoding, errors=errors)
    if non_string == 'empty':
        return u''
    elif non_string == 'passthru':
        return obj
    elif non_string == 'simplerepr':
        try:
            simple = obj.__unicode__()
        except AttributeError:
            simple = None
        if not simple:
            try:
                simple = obj.__str__()
            except (UnicodeError, AttributeError):
                simple = u''
        if not isinstance(simple, unicode):
            return to_unicode(simple, 'utf8', 'replace')
        return simple
    elif non_string in ('repr', 'strict'):
        obj_repr = repr(obj)
        if not isinstance(obj_repr, unicode):
            unicode(obj_repr, encoding=encoding, errors=errors)
        if non_string == 'repr':
            return obj_repr
        raise TypeError(_('to_unicode was given "%(obj)s" which is neither'
            ' a byte string (str) or a unicode string') % {'obj': obj_repr})

    raise TypeError(_('non_string value, %(param)s, is not set to a valid'
        ' action') % {'param': non_string})

def to_bytes(obj, encoding='utf8', errors='replace', non_string='empty'):
    '''Convert an object into a byte string

    Usually, this should be used on a unicode string but it can take byte
    strings and unicode strings intelligently.  non_string objects are handled
    in different ways depending on the setting of the non_string parameter.

    The default values of this function are set so as to always return
    a byte string and never raise an error when converting from unicode to
    bytes.  However, when you do not pass an encoding that can validly encode
    the object (or a non-string object), you may end up with output that you
    don't expect.  Be sure you understand the requirements of your data, not
    just ignore errors by passing it through this function.

    :arg obj: Object to convert to a byte string.  This should normally be
        a unicode string.
    :kwarg encoding: Encoding to use to convert the unicode string into
        bytes.  **Warning**: if you pass a byte string into this function the
        byte string is returned unmodified.  It is not re-encoded with this
        encoding.  Defaults to utf8.
    :kwarg errors: If errors are found when encoding, perform this action.
        Defaults to 'replace' which replaces the error with a '?' character to
        show a character was unable to be encoded.  Other values are those
        that can be given to the :func:`str.encode`.  For instance
        'strict' which raises an exception and 'ignore' which simply omits the
        non-encodable characters.
    :kwargs non_string: How to treat non_string values.  Possible values are:
            :empty: Return an empty byte string
            :strict: Raise a TypeError
            :passthru: Return the object unchanged
            :simplerepr: Attempt to call the object's "simple representation"
                method and return that value.  Python-2.3+ has two methods
                that try to return a simple representation: __unicode__() and
                __str__().  We first try to get a usable value from
                __str__().  If that fails we try the same with __unicode__().
            :repr: Attempt to return a byte string of the repr of the
                object
        The Default is 'empty'
    :raises TypeError: if :attr:`non_string` is strict and a non-basestring
        object is passed in or if :attr:`non_string` is set to an unknown
        value.
    :raises UnicodeEncodeError: if :attr:`errors` is strict and all of the
        bytes of obj are unable to be encoded using :attr:`encoding`.
    :returns: byte string or the original object depending on the value of
        non_string.
    '''
    if isinstance(obj, basestring):
        if isinstance(obj, str):
            return obj
        return obj.encode(encoding, errors)
    if non_string == 'empty':
        return ''
    elif non_string == 'passthru':
        return obj
    elif non_string == 'simplerepr':
        try:
            simple = obj.__str__()
        except (AttributeError, UnicodeError):
            simple = None
        if not simple:
            try:
                simple = obj.__unicode__()
            except AttributeError:
                simple = ''
        if isinstance(simple, unicode):
            simple = simple.encode(encoding, 'replace')
        return simple
    elif non_string in ('repr', 'strict'):
        obj_repr = repr(obj)
        if isinstance(obj_repr, unicode):
            obj_repr =  obj_repr.encode(encoding, errors)
        else:
            obj_repr = str(obj_repr)
        if non_string == 'repr':
            return obj_repr
        raise TypeError(_('to_bytes was given "%(obj)s" which is neither'
            ' a unicode string or a byte string (str)') % {'obj': obj_repr})

    raise TypeError(_('non_string value, %(param)s, is not set to a valid'
        ' action') % {'param': non_string})

### skvidal: Will changing behaviour from passthru to empty cause issues for yum?
#def to_unicode(obj, encoding='utf-8', errors='replace', non_string='passthru'):
#    ''' convert a 'str' to 'unicode' '''
#    if isinstance(obj, basestring):
#        if not isinstance(obj, unicode):
#            obj = unicode(obj, encoding, errors)
#    return obj

def to_utf8(obj, errors='replace', non_string='passthru'):
    '''Deprecated.  Use to_bytes(obj, encoding='utf8', non_string='passthru')

    Convert 'unicode' to an encoded utf-8 byte string
    '''
    warnings.warn(_('kitchen.text.to_utf8 is deprecated.  Use'
        ' kitchen.text.to_bytes(obj, encoding="utf8", non_string="passthru")'
        ' instead.'), DeprecationWarning, stacklevel=2)
    return to_bytes(obj, encoding='utf8', errors='replace',
            non_string=non_string)

### str is also the type name for byte strings so it's not a good name for
### something that can return unicode strings
def to_str(obj):
    '''Deprecated.

    This function converts something to a byte string if it isn't one.
    It's used to call str() or unicode() on the object to get its simple
    representation without danger of getting a UnicodeError.  You
    should be using :func:`to_unicode` or :func:`to_bytes` explicitly
    instead.  If you need unicode strings::

        to_unicode(obj, non_string='simplerepr')

    If you need byte strings::

        to_bytes(obj, non_string='simplerepr')
    '''
    warnings.warn(_('to_str is deprecated.  Use to_unicode or to_bytes'
        ' instead.  See the string_representation docstring for'
        ' porting information.'),
        DeprecationWarning, stacklevel=2)
    return to_bytes(obj, non_string='simplerepr')

def str_eq(str1, str2, encoding='utf8', errors='replace'):
    """Compare two strings even if one is a byte string and one is unicode

    :arg str1: first string to compare
    :arg str2: second string to compare
    :kwarg encoding: If we need to convert one string into a byte string to
        compare, the encoding to use.  Default is utf8.
    :kwarg errors: If we encounter errors when encoding the string, what to
        do.  See the :func:`to_bytes` documentation for possible values.
        The default is 'replace'

    This function prevents UnicodeErrors when we compare a unicode string to
    a byte string.  The errors normally arise because the conversion is done
    to ASCII.  This function lets you convert to utf8 or another encoding
    instead.

    Note that when we need to convert one of the strings from unicode in order
    to compare them we convert the unicode string into a byte string.  That
    means that strings can compare differently if you use different encodings
    for each.
    """
    if isinstance(str1, unicode) == isinstance(str2, unicode):
        if str1 == str2:
            return True
    elif to_bytes(str1, encoding=encoding, errors=errors)\
            == to_bytes(str2, encoding=encoding, errors=errors):
        return True

    return False

__all__ = ('guess_encoding', 'str_eq', 'to_bytes', 'to_str', 'to_unicode',
        'to_utf8',)
