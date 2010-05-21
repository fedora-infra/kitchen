# -*- coding: utf-8 -*-
# Copyright (c) 2010 Red Hat, Inc
# Copyright (c) 2010 Seth Vidal
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
#   James Antill
#   Toshio Kuratomi <toshio@fedoraproject.org>
#   Seth Vidal
#
# Portions of this code taken from yum/misc.py and yum/i18n.py
'''Miscellaneous functions for manipulating text.
'''
import htmlentitydefs
import itertools
import re

try:
    import chardet
except ImportError:
    chardet = None

from kitchen import _
from kitchen.pycompat24 import builtinset
from kitchen.text.exceptions import ControlCharError

builtinset.add_builtin_set()

# Define a threshold for chardet confidence.  If we fall below this we decode
# byte strings we're guessing about as latin1
_chardet_threshhold = 0.6

# ASCII control codes that are illegal in xml 1.0
_control_codes = frozenset(range(0, 8) + [11, 12] + range(14, 32))
_control_chars = frozenset(itertools.imap(unichr, _control_codes))

# _ENTITY_RE
_ENTITY_RE = re.compile(r'(?s)<[^>]*>|&#?\w+;')

def guess_encoding(byte_string, disable_chardet=False):
    '''Try to guess the encoding of a byte_string

    :arg byte_string: byte_string to guess the encoding of
    :kwarg disable_chardet: If this is True, we never attempt to use
        :mod:`chardet` to guess the encoding.  This is useful if you need to
        have reproducability whether chardet is installed or not.  Default:
        False.
    :raises TypeError: if byte_string is not a byte string (str) type
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
        raise TypeError(_('byte_string must be a byte string (str)'))
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

def str_eq(str1, str2, encoding='utf8', errors='replace'):
    '''Compare two strings even if one is a byte string and one is unicode

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
    '''
    # Import this here to avoid circular deps
    from kitchen.text.converters import to_bytes
    if isinstance(str1, unicode) == isinstance(str2, unicode):
        if str1 == str2:
            return True
    elif to_bytes(str1, encoding=encoding, errors=errors)\
            == to_bytes(str2, encoding=encoding, errors=errors):
        return True

    return False

def process_control_chars(string, strategy='replace'):
    '''Look for and transform control characters in a string

    :arg string: string to search for and transform control characters in
    :kwarg strategy: XML does not allow ASCII control characters.  When
        we encounter those we need to know what to do.  Valid options are:
        :replace: (default) Replace the control characters with "?"
        :ignore: Remove the characters altogether from the output
        :strict: Raise an error when we encounter a control character
    :raises TypeError: if :attr:`string` is not a unicode string.
    :raises ValueError: if the strategy is not one of replace, ignore, or
        strict.
    :returns: unicode string with no control characters in it.
    '''
    if not isinstance(string, unicode):
        raise TypeError(_('process_control_char must have a unicode type as'
                ' the first argument.'))
    if strategy == 'ignore':
        control_table = dict(zip(_control_codes, [None] * len(_control_codes)))
    elif strategy == 'replace':
        control_table = dict(zip(_control_codes, [u'?'] * len(_control_codes)))
    elif strategy == 'strict':
        control_table = None
        # Test that there are no control codes present
        data = frozenset(string)
        if [c for c in _control_chars if c in data]:
            raise ControlCharError(_('ASCII control code present in string'
                    ' input'))
    else:
        raise ValueError(_('The strategy argument to process_control_chars'
                ' must be one of ignore, replace, or strict'))

    if control_table:
        string = string.translate(control_table)

    return string

# Originally written by Fredrik Lundh (January 15, 2003) and placed in the
# public domain::
#
#   Unless otherwise noted, source code can be be used freely. Examples, test
#   scripts and other short code fragments can be considered as being in the
#   public domain.
#
# http://effbot.org/zone/re-sub.htm#unescape-html
# http://effbot.org/zone/copyright.htm
#
def html_entities_unescape(string):
    '''Substitute unicode characters for HTML entities

    :arg string: Unicode string to substitute out html entities
    :raises TypeError: if something other than a unicode string is given
    :rtype: unicode string
    :returns: The plain text.  If the HTML source contains non-ASCII
      entities or character references, this is a Unicode string.
    '''
    def fixup(m):
        string = m.group(0)
        if string[:1] == "<":
            return "" # ignore tags
        if string[:2] == "&#":
            try:
                if string[:3] == "&#x":
                    return unichr(int(string[3:-1], 16))
                else:
                    return unichr(int(string[2:-1]))
            except ValueError:
                pass
        elif string[:1] == "&":
            entity = htmlentitydefs.entitydefs.get(string[1:-1])
            if entity:
                if entity[:2] == "&#":
                    try:
                        return unichr(int(entity[2:-1]))
                    except ValueError:
                        pass
                else:
                    return unicode(entity, "iso-8859-1")
        return string # leave as is

    if not isinstance(string, unicode):
        raise TypeError(_('html_entities_unescape must have a unicode type'
                ' for its first argument'))
    return re.sub(_ENTITY_RE, fixup, string)

def byte_string_valid_xml(byte_string, encoding='utf8'):
    '''Check that a byte string would be valid in xml

    :arg byte_string: Byte string to check
    :arg encoding: Encoding of the xml file.  Default: utf8
    :returns: True if the string is valid, False if it would be invalid in the
        xml file

    In some cases you'll have a whole bunch of byte strings and rather than
    transforming them to unicode and back to byte strings for output to
    xml, you will just want to make sure they work with the xml file you're
    constructing.  This function will help you do that::

        ARRAY_OF_MOSTLY_UTF8_STRINGS = [...]
        processed_array = []
        for string in ARRAY_OF_MOSTLY_UTF8_STRINGS:
            if byte_string_valid_xml(string, 'utf8'):
                processed_array.append(string)
            else:
                processed_array.append(guess_bytes_to_xml(string, encoding='utf8'))
        output_xml(processed_array)
    '''
    if not isinstance(byte_string, str):
        # Not a byte string
        return False

    try:
        unicode(byte_string, encoding)
    except UnicodeError:
        # Not encoded with the xml file's encoding
        return False

    data = frozenset(byte_string)
    if data.intersection(_control_chars):
        # Contains control codes
        return False

    # The byte string is compatible with this xml file
    return True

__all__ = ('byte_string_valid_xml', 'guess_encoding',
        'html_entities_unescape', 'process_control_chars', 'str_eq')
