# -*- coding: utf-8 -*-
#
# Copyright (c) 2010 Red Hat, Inc.
# Copyright (c) 2010 Ville Skyttä
# Copyright (c) 2009 Tim Lauridsen
# Copyright (c) 2007 Marcus Kuhn
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
#   James Antill <james@fedoraproject.org>
#   Marcus Kuhn
#   Toshio Kuratomi <toshio@fedoraproject.org>
#   Tim Lauridsen
#   Ville Skyttä
#
# Portions of this are from yum/i18n.py
'''
-----
UTF-8
-----

Functions for operating on byte :class:`str` encoded as :term:`utf8`

.. note:: In many cases, it is better to convert to :class:`unicode`, operate
    on the strings, then convert back to :term:`utf8`.  :class:`unicode` type
    can handle many of these functions itself.  For those that it doesn't
    (removing control characters from length calculations, for instance) the
    code to do so with a :class:`unicode` type is often simpler.
'''
import warnings

from kitchen import _
from kitchen.text.converters import to_unicode, to_bytes
from kitchen.text.misc import byte_string_valid_encoding
from kitchen.text.display import _textual_width_le, \
        byte_string_textual_width_fill, fill, textual_width, \
        textual_width_chop, wrap

# JA's port of MK's code
def _iter_bytes_as_ints(msg):
    '''Iterate through the byte :class:`str`, returning bytes as ints

    :arg msg: byte :class:`str` to iterate through
    :rtype: int
    :returns: integer representation of the next byte
    '''
    for byte in to_bytes(msg):
        yield ord(byte)

# JA's port of MK's C code
def _iter_ucs(msg):
    '''Iterate through the string, returning codepoint and number of bytes

    :arg msg: byte :class:`str` to take :term:`code point`s from
    :rtype: tuple
    :returns: tuple of unicode :term:`code point` and number of bytes consumed
        to make that :term:`code point`

    On error, this function returns None as the first entry in the tuple.  The
    second entry contains the number of bytes that were read from the string
    before determining this sequence of bytes did not form a character.
    '''
    uiter = _iter_bytes_as_ints(msg)
    for byte0 in uiter:
        if byte0 < 0x80:             # 0xxxxxxx
            yield (byte0, 1)
        elif (byte0 & 0xe0) == 0xc0: # 110XXXXx 10xxxxxx
            try:
                byte1 = uiter.next()
            except StopIteration:
                # Too short
                yield(None, 1)
                return
            if (((byte1 & 0xc0) != 0x80) or
                ((byte0 & 0xfe) == 0xc0)):                          # overlong?
                yield (None, 2)
                return
            yield ((((byte0 & 0x1f) << 6) | (byte1 & 0x3f)), 2)
        elif (byte0 & 0xf0) == 0xe0: # 1110XXXX 10Xxxxxx 10xxxxxx
            bytes = [byte0]
            for byte_count in range(1,3):
                try:
                    bytes.append(uiter.next())
                except StopIteration:
                    # If this is triggered, the byte sequence is too short
                    yield (None, byte_count)
                    return
            if (((bytes[1] & 0xc0) != 0x80) or ((bytes[2] & 0xc0) != 0x80) or
                ((bytes[0] == 0xe0) and ((bytes[1] & 0xe0) == 0x80)) or   # overlong?
                ((bytes[0] == 0xed) and ((bytes[1] & 0xe0) == 0xa0)) or   # surrogate?
                ((bytes[0] == 0xef) and  (bytes[1] == 0xbf) and
                 ((bytes[2] & 0xfe) == 0xbe))): # U+FFFE or U+FFFF?
                yield (None, 3)
                return
            yield ((((bytes[0] & 0x0f) << 12) | ((bytes[1] & 0x3f) << 6) |
                   (bytes[2] & 0x3f)), 3)
        elif (byte0 & 0xf8) == 0xf0: # 11110XXX 10XXxxxx 10xxxxxx 10xxxxxx
            bytes = [byte0]
            for byte_count in range(1,4):
                try:
                    bytes.append(uiter.next())
                except StopIteration:
                    # If this is triggered, the byte sequence is too short
                    yield (None, byte_count)
                    return
            if (((bytes[1] & 0xc0) != 0x80) or
                ((bytes[2] & 0xc0) != 0x80) or
                ((bytes[3] & 0xc0) != 0x80) or
                ((bytes[0] == 0xf0) and ((bytes[1] & 0xf0) == 0x80)) or # overlong?
                ((bytes[0] == 0xf4) and (bytes[1] > 0x8f)) or           # > U+10FFFF?
                (bytes[0] > 0xf4)):                                  # > U+10FFFF?
                yield (None, 4)
                return

            yield ((((bytes[0] & 0x07) << 18) | ((bytes[1] & 0x3f) << 12) |
                    ((bytes[2] & 0x3f) <<  6) |  (bytes[3] & 0x3f)), 4)
        else:
            yield (None, 1)
            return


# ----------------------------- END utf8 -----------------------------

#
# Deprecated functions
#

def utf8_valid(msg):
    '''Deprecated.  Detect if a string is valid utf8.

    Use :func:`kitchen.text.misc.byte_string_valid_encoding` instead.
    '''
    warnings.warn(_('Deprecated.  Use'
            ' kitchen.text.misc.byte_string_valid_encoding(msg) instead'),
            DeprecationWarning, stacklevel=2)
    return byte_string_valid_encoding(msg)

def utf8_width(msg):
    '''Deprecated

    Use :func:`~kitchen.text.utf8.textual_width` instead.
    '''
    warnings.warn(_('kitchen.text.utf8.utf8_width is deprecated.  Use'
        ' kitchen.text.utf8.textual_width(msg) instead'), DeprecationWarning,
        stacklevel=2)
    return textual_width(msg)


def utf8_width_chop(msg, chop=None):
    '''Deprecated

    Use :func:`~kitchen.text.utf8.textual_width_chop` and
    :func:`~kitchen.textt.utf8.textual_width` instead::

        >>> msg = 'く ku ら ra と to み mi'
        >>> # Old way:
        >>> utf8_width_chop(msg, 5)
        (5, 'く ku')
        >>> # New way
        >>> from kitchen.text.converters import to_bytes
        >>> from kitchen.utf8 import textual_width, textual_width_chop
        >>> (textual_width(msg), to_bytes(textual_width_chop(msg, 5)))
        (5, 'く ku')
    '''
    warnings.warn(_('kitchen.text.utf8.utf8_width_chop is deprecated.  Use'
        ' kitchen.text.utf8.textual_width_chop instead'), DeprecationWarning,
        stacklevel=2)

    if chop == None:
        return textual_width(msg), msg

    as_bytes = not isinstance(msg, unicode)
 
    chopped_msg = textual_width_chop(msg, chop)
    if as_bytes:
        chopped_msg = to_bytes(chopped_msg)
    return textual_width(chopped_msg), chopped_msg

def utf8_width_fill(msg, fill, chop=None, left=True, prefix='', suffix=''):
    '''Deprecated.

    Use :func:`~kitchen.text.utf8.byte_string_textual_width_fill` instead
    '''
    warnings.warn(_('kitchen.text.utf8.utf8_width_fill is deprecated.  Use'
        ' kitchen.text.utf8.byte_string_textual_width_fill instead'),
        DeprecationWarning, stacklevel=2)

    return byte_string_textual_width_fill(msg, fill, chop=chop, left=left,
            prefix=prefix, suffix=suffix)

def utf8_text_wrap(text, width=70, initial_indent='', subsequent_indent=''):
    '''Deprecated.

    Use :func:`~kitchen.text.display.wrap` instead
    '''
    warnings.warn(_('kitchen.text.utf8.utf8_text_wrap is deprecated.  Use'
        ' kitchen.text.display.wrap instead'),
        DeprecationWarning, stacklevel=2)

    as_bytes = not isinstance(text, unicode)

    text = to_unicode(text)
    lines = wrap(text, width=width, initial_indent=initial_indent,
            subsequent_indent=subsequent_indent)
    if as_bytes:
        lines = [to_bytes(m) for m in lines]

    return lines

def utf8_text_fill(text, *args, **kwargs):
    '''**Deprecated**  Use :func:`kitchen.text.display.fill` instead.'''
    warnings.warn(_('kitchen.text.utf8.utf8_text_fill is deprecated.  Use'
        ' kitchen.text.display.fill instead'),
        DeprecationWarning, stacklevel=2)
    # This assumes that all args. are utf8.
    return fill(text, *args, **kwargs)

def _utf8_width_le(width, *args):
    '''**Deprecated** Convert the arguments to unicode and use
    :func:`_textual_width_le` instead.
    '''
    warnings.warn(_('kitchen.text.utf8._utf8_width_le is deprecated.  Use'
        ' kitchen.text.utf8._textual_width_le instead'),
        DeprecationWarning, stacklevel=2)
    # This assumes that all args. are utf8.
    return _textual_width_le(width, to_unicode(''.join(args)))

__all__ = ('utf8_text_fill', 'utf8_text_wrap', 'utf8_valid', 'utf8_width',
        'utf8_width_chop', 'utf8_width_fill')
