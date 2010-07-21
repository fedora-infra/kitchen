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
import itertools
import unicodedata
import warnings

from kitchen import _
from kitchen.text.converters import to_unicode, to_bytes
from kitchen.text.exceptions import ControlCharError
from kitchen.text.misc import byte_string_valid_encoding

# This is ported from ustr_utf8_* which I got from:
#     http://www.cl.cam.ac.uk/~mgk25/ucs/wcwidth.c
#  I've tried to leave it close to the original C (same names etc.) so that
# it is easy to read/compare both versions... James Antilles

#
# Reimplemented quite a bit of this for speed.  Use the bzr log or annotate
# commands to see what I've changed since importing this file.-Toshio Kuratomi

# ----------------------------- BEG utf8 ------------------to-----------
# This is an implementation of wcwidth() and wcswidth() (defined in
# IEEE Std 1002.1-2001) for Unicode.
#
# http://www.opengroup.org/onlinepubs/007904975/functions/wcwidth.html
# http://www.opengroup.org/onlinepubs/007904975/functions/wcswidth.html
#
# In fixed-width output devices, Latin characters all occupy a single
# "cell" position of equal width, whereas ideographic CJK characters
# occupy two such cells. Interoperability between terminal-line
# applications and (teletype-style) character terminals using the
# UTF-8 encoding requires agreement on which character should advance
# the cursor by how many cell positions. No established formal
# standards exist at present on which Unicode character shall occupy
# how many cell positions on character terminals. These routines are
# a first attempt of defining such behavior based on simple rules
# applied to data provided by the Unicode Consortium.
#
# [...]
#
# Markus Kuhn -- 2007-05-26 (Unicode 5.0)
#
# Permission to use, copy, modify, and distribute this software
# for any purpose and without fee is hereby granted. The author
# disclaims all warranties with regard to this software.
#
# Latest version: http://www.cl.cam.ac.uk/~mgk25/ucs/wcwidth.c

# Renamed but still pretty much JA's port of MK's code
def _interval_bisearch(value, table):
    '''Binary search in an interval table.

    This function checks whether a numeric value is present within a table
    of intervals.  It checks using a binary search algorithm, dividing the
    list of values in half and checking against the values until it determines
    whether the value is in the table.

    :arg value: numeric value to search for
    :arg table: Ordered list of intervals.  This is a list of two-tuples.  The
        elements of the two-tuple define an interval's start and end points.
    :returns: If :attr:`value` is found within an interval in the :attr:`table`
        return True.  Otherwise, False
    '''
    minimum = 0
    maximum = len(table) - 1
    if value < table[minimum][0] or value > table[maximum][1]:
        return False

    while maximum >= minimum:
        mid = (minimum + maximum) / 2
        if value > table[mid][1]:
            minimum = mid + 1
        elif value < table[mid][0]:
            maximum = mid - 1
        else:
            return True

    return False

#: Internal table, provided by this module to list :term:`code points` which
# combine with other characters and therefore should have no :term:`textual
# width`.  This is a sorted tuple of non-overlapping intervals.  Each interval
# is a tuple listing a starting :term:`code point` and ending
# :term:`code point`.  Every :term:`code point` between the two end points is
# a combining character.
#
# .. seealso::
#   `~kitchen.text.utf8._generate_combining_table`
#       for how this table is generated
#
# This table was last regenerated on python-2.6.4 with
# :data:`unicodedata.unicodedata_version` 5.1.0

_COMBINING = (
        ( 0x300, 0x36f ), ( 0x483, 0x489 ), ( 0x591, 0x5bd ),
        ( 0x5bf, 0x5bf ), ( 0x5c1, 0x5c2 ), ( 0x5c4, 0x5c5 ),
        ( 0x5c7, 0x5c7 ), ( 0x600, 0x603 ), ( 0x610, 0x61a ),
        ( 0x64b, 0x65e ), ( 0x670, 0x670 ), ( 0x6d6, 0x6e4 ),
        ( 0x6e7, 0x6e8 ), ( 0x6ea, 0x6ed ), ( 0x70f, 0x70f ),
        ( 0x711, 0x711 ), ( 0x730, 0x74a ), ( 0x7a6, 0x7b0 ),
        ( 0x7eb, 0x7f3 ), ( 0x901, 0x902 ), ( 0x93c, 0x93c ),
        ( 0x941, 0x948 ), ( 0x94d, 0x94d ), ( 0x951, 0x954 ),
        ( 0x962, 0x963 ), ( 0x981, 0x981 ), ( 0x9bc, 0x9bc ),
        ( 0x9c1, 0x9c4 ), ( 0x9cd, 0x9cd ), ( 0x9e2, 0x9e3 ),
        ( 0xa01, 0xa02 ), ( 0xa3c, 0xa3c ), ( 0xa41, 0xa42 ),
        ( 0xa47, 0xa48 ), ( 0xa4b, 0xa4d ), ( 0xa70, 0xa71 ),
        ( 0xa81, 0xa82 ), ( 0xabc, 0xabc ), ( 0xac1, 0xac5 ),
        ( 0xac7, 0xac8 ), ( 0xacd, 0xacd ), ( 0xae2, 0xae3 ),
        ( 0xb01, 0xb01 ), ( 0xb3c, 0xb3c ), ( 0xb3f, 0xb3f ),
        ( 0xb41, 0xb43 ), ( 0xb4d, 0xb4d ), ( 0xb56, 0xb56 ),
        ( 0xb82, 0xb82 ), ( 0xbc0, 0xbc0 ), ( 0xbcd, 0xbcd ),
        ( 0xc3e, 0xc40 ), ( 0xc46, 0xc48 ), ( 0xc4a, 0xc4d ),
        ( 0xc55, 0xc56 ), ( 0xcbc, 0xcbc ), ( 0xcbf, 0xcbf ),
        ( 0xcc6, 0xcc6 ), ( 0xccc, 0xccd ), ( 0xce2, 0xce3 ),
        ( 0xd41, 0xd43 ), ( 0xd4d, 0xd4d ), ( 0xdca, 0xdca ),
        ( 0xdd2, 0xdd4 ), ( 0xdd6, 0xdd6 ), ( 0xe31, 0xe31 ),
        ( 0xe34, 0xe3a ), ( 0xe47, 0xe4e ), ( 0xeb1, 0xeb1 ),
        ( 0xeb4, 0xeb9 ), ( 0xebb, 0xebc ), ( 0xec8, 0xecd ),
        ( 0xf18, 0xf19 ), ( 0xf35, 0xf35 ), ( 0xf37, 0xf37 ),
        ( 0xf39, 0xf39 ), ( 0xf71, 0xf7e ), ( 0xf80, 0xf84 ),
        ( 0xf86, 0xf87 ), ( 0xf90, 0xf97 ), ( 0xf99, 0xfbc ),
        ( 0xfc6, 0xfc6 ), ( 0x102d, 0x1030 ), ( 0x1032, 0x1032 ),
        ( 0x1036, 0x1037 ), ( 0x1039, 0x103a ), ( 0x1058, 0x1059 ),
        ( 0x108d, 0x108d ), ( 0x1160, 0x11ff ), ( 0x135f, 0x135f ),
        ( 0x1712, 0x1714 ), ( 0x1732, 0x1734 ), ( 0x1752, 0x1753 ),
        ( 0x1772, 0x1773 ), ( 0x17b4, 0x17b5 ), ( 0x17b7, 0x17bd ),
        ( 0x17c6, 0x17c6 ), ( 0x17c9, 0x17d3 ), ( 0x17dd, 0x17dd ),
        ( 0x180b, 0x180d ), ( 0x18a9, 0x18a9 ), ( 0x1920, 0x1922 ),
        ( 0x1927, 0x1928 ), ( 0x1932, 0x1932 ), ( 0x1939, 0x193b ),
        ( 0x1a17, 0x1a18 ), ( 0x1b00, 0x1b03 ), ( 0x1b34, 0x1b34 ),
        ( 0x1b36, 0x1b3a ), ( 0x1b3c, 0x1b3c ), ( 0x1b42, 0x1b42 ),
        ( 0x1b44, 0x1b44 ), ( 0x1b6b, 0x1b73 ), ( 0x1baa, 0x1baa ),
        ( 0x1c37, 0x1c37 ), ( 0x1dc0, 0x1de6 ), ( 0x1dfe, 0x1dff ),
        ( 0x200b, 0x200f ), ( 0x202a, 0x202e ), ( 0x2060, 0x2063 ),
        ( 0x206a, 0x206f ), ( 0x20d0, 0x20f0 ), ( 0x2de0, 0x2dff ),
        ( 0x302a, 0x302f ), ( 0x3099, 0x309a ), ( 0xa66f, 0xa66f ),
        ( 0xa67c, 0xa67d ), ( 0xa806, 0xa806 ), ( 0xa80b, 0xa80b ),
        ( 0xa825, 0xa826 ), ( 0xa8c4, 0xa8c4 ), ( 0xa92b, 0xa92d ),
        ( 0xa953, 0xa953 ), ( 0xfb1e, 0xfb1e ), ( 0xfe00, 0xfe0f ),
        ( 0xfe20, 0xfe26 ), ( 0xfeff, 0xfeff ), ( 0xfff9, 0xfffb ),
        ( 0x101fd, 0x101fd ), ( 0x10a01, 0x10a03 ), ( 0x10a05, 0x10a06 ),
        ( 0x10a0c, 0x10a0f ), ( 0x10a38, 0x10a3a ), ( 0x10a3f, 0x10a3f ),
        ( 0x1d165, 0x1d169 ), ( 0x1d16d, 0x1d182 ), ( 0x1d185, 0x1d18b ),
        ( 0x1d1aa, 0x1d1ad ), ( 0x1d242, 0x1d244 ), ( 0xe0001, 0xe0001 ),
        ( 0xe0020, 0xe007f ), ( 0xe0100, 0xe01ef ),
    )

# New function from Toshio Kuratomi (LGPLv2+)
def _generate_combining_table():
    '''Combine Markus Kuhn's data with unicodedata to make combining char list

    :rtype: tuple of tuples
    :returns: A list of intervals of :term:`code points` that are combining
        character.  Each interval is a 2-tuple of the starting
        :term:`code point` and the ending :term:`code point` for the combining
        characters.

    In normal use, this function serves to tell how we're generating the
    combining char list.  For speed reasons, we use this to generate a static
    list and just use that later.

    Markus Kuhn's list of combining characters is more complete than what's in
    the python :mod:`unicodedata` library but the python :mod:`unicodedata` is
    synced against later versions of the unicode database

    This is used to generate the :data:`~kitchen.text.utf8._COMBINING` table
    using roughly the following code::

        from kitchen.text.utf8 import _generate_combining_table
        table = _generate_combining_table()
        for interval in table:
            print '( %s, %s ),' % (hex(interval[0]), hex(interval[1]))
    '''
    # Marcus Kuhn's sorted list of non-overlapping intervals of non-spacing
    # characters generated ifrom Unicode 5.0 data by:
    # "uniset +cat=Me +cat=Mn +cat=Cf -00AD +1160-11FF +200B c"
    markus_kuhn_combining_5_0 = (
        ( 0x0300, 0x036F ), ( 0x0483, 0x0486 ), ( 0x0488, 0x0489 ),
        ( 0x0591, 0x05BD ), ( 0x05BF, 0x05BF ), ( 0x05C1, 0x05C2 ),
        ( 0x05C4, 0x05C5 ), ( 0x05C7, 0x05C7 ), ( 0x0600, 0x0603 ),
        ( 0x0610, 0x0615 ), ( 0x064B, 0x065E ), ( 0x0670, 0x0670 ),
        ( 0x06D6, 0x06E4 ), ( 0x06E7, 0x06E8 ), ( 0x06EA, 0x06ED ),
        ( 0x070F, 0x070F ), ( 0x0711, 0x0711 ), ( 0x0730, 0x074A ),
        ( 0x07A6, 0x07B0 ), ( 0x07EB, 0x07F3 ), ( 0x0901, 0x0902 ),
        ( 0x093C, 0x093C ), ( 0x0941, 0x0948 ), ( 0x094D, 0x094D ),
        ( 0x0951, 0x0954 ), ( 0x0962, 0x0963 ), ( 0x0981, 0x0981 ),
        ( 0x09BC, 0x09BC ), ( 0x09C1, 0x09C4 ), ( 0x09CD, 0x09CD ),
        ( 0x09E2, 0x09E3 ), ( 0x0A01, 0x0A02 ), ( 0x0A3C, 0x0A3C ),
        ( 0x0A41, 0x0A42 ), ( 0x0A47, 0x0A48 ), ( 0x0A4B, 0x0A4D ),
        ( 0x0A70, 0x0A71 ), ( 0x0A81, 0x0A82 ), ( 0x0ABC, 0x0ABC ),
        ( 0x0AC1, 0x0AC5 ), ( 0x0AC7, 0x0AC8 ), ( 0x0ACD, 0x0ACD ),
        ( 0x0AE2, 0x0AE3 ), ( 0x0B01, 0x0B01 ), ( 0x0B3C, 0x0B3C ),
        ( 0x0B3F, 0x0B3F ), ( 0x0B41, 0x0B43 ), ( 0x0B4D, 0x0B4D ),
        ( 0x0B56, 0x0B56 ), ( 0x0B82, 0x0B82 ), ( 0x0BC0, 0x0BC0 ),
        ( 0x0BCD, 0x0BCD ), ( 0x0C3E, 0x0C40 ), ( 0x0C46, 0x0C48 ),
        ( 0x0C4A, 0x0C4D ), ( 0x0C55, 0x0C56 ), ( 0x0CBC, 0x0CBC ),
        ( 0x0CBF, 0x0CBF ), ( 0x0CC6, 0x0CC6 ), ( 0x0CCC, 0x0CCD ),
        ( 0x0CE2, 0x0CE3 ), ( 0x0D41, 0x0D43 ), ( 0x0D4D, 0x0D4D ),
        ( 0x0DCA, 0x0DCA ), ( 0x0DD2, 0x0DD4 ), ( 0x0DD6, 0x0DD6 ),
        ( 0x0E31, 0x0E31 ), ( 0x0E34, 0x0E3A ), ( 0x0E47, 0x0E4E ),
        ( 0x0EB1, 0x0EB1 ), ( 0x0EB4, 0x0EB9 ), ( 0x0EBB, 0x0EBC ),
        ( 0x0EC8, 0x0ECD ), ( 0x0F18, 0x0F19 ), ( 0x0F35, 0x0F35 ),
        ( 0x0F37, 0x0F37 ), ( 0x0F39, 0x0F39 ), ( 0x0F71, 0x0F7E ),
        ( 0x0F80, 0x0F84 ), ( 0x0F86, 0x0F87 ), ( 0x0F90, 0x0F97 ),
        ( 0x0F99, 0x0FBC ), ( 0x0FC6, 0x0FC6 ), ( 0x102D, 0x1030 ),
        ( 0x1032, 0x1032 ), ( 0x1036, 0x1037 ), ( 0x1039, 0x1039 ),
        ( 0x1058, 0x1059 ), ( 0x1160, 0x11FF ), ( 0x135F, 0x135F ),
        ( 0x1712, 0x1714 ), ( 0x1732, 0x1734 ), ( 0x1752, 0x1753 ),
        ( 0x1772, 0x1773 ), ( 0x17B4, 0x17B5 ), ( 0x17B7, 0x17BD ),
        ( 0x17C6, 0x17C6 ), ( 0x17C9, 0x17D3 ), ( 0x17DD, 0x17DD ),
        ( 0x180B, 0x180D ), ( 0x18A9, 0x18A9 ), ( 0x1920, 0x1922 ),
        ( 0x1927, 0x1928 ), ( 0x1932, 0x1932 ), ( 0x1939, 0x193B ),
        ( 0x1A17, 0x1A18 ), ( 0x1B00, 0x1B03 ), ( 0x1B34, 0x1B34 ),
        ( 0x1B36, 0x1B3A ), ( 0x1B3C, 0x1B3C ), ( 0x1B42, 0x1B42 ),
        ( 0x1B6B, 0x1B73 ), ( 0x1DC0, 0x1DCA ), ( 0x1DFE, 0x1DFF ),
        ( 0x200B, 0x200F ), ( 0x202A, 0x202E ), ( 0x2060, 0x2063 ),
        ( 0x206A, 0x206F ), ( 0x20D0, 0x20EF ), ( 0x302A, 0x302F ),
        ( 0x3099, 0x309A ), ( 0xA806, 0xA806 ), ( 0xA80B, 0xA80B ),
        ( 0xA825, 0xA826 ), ( 0xFB1E, 0xFB1E ), ( 0xFE00, 0xFE0F ),
        ( 0xFE20, 0xFE23 ), ( 0xFEFF, 0xFEFF ), ( 0xFFF9, 0xFFFB ),
        ( 0x10A01, 0x10A03 ), ( 0x10A05, 0x10A06 ), ( 0x10A0C, 0x10A0F ),
        ( 0x10A38, 0x10A3A ), ( 0x10A3F, 0x10A3F ), ( 0x1D167, 0x1D169 ),
        ( 0x1D173, 0x1D182 ), ( 0x1D185, 0x1D18B ), ( 0x1D1AA, 0x1D1AD ),
        ( 0x1D242, 0x1D244 ), ( 0xE0001, 0xE0001 ), ( 0xE0020, 0xE007F ),
        ( 0xE0100, 0xE01EF ))
    combining = []
    in_interval = False
    interval = []
    for codepoint in xrange (0, 0xFFFFF + 1):
        if _interval_bisearch(codepoint, markus_kuhn_combining_5_0) or \
                unicodedata.combining(unichr(codepoint)):
            if not in_interval:
                # Found first part of an interval
                interval = [codepoint]
                in_interval = True
        else:
            if in_interval:
                in_interval = False
                interval.append(codepoint - 1)
                combining.append(interval)
    if in_interval:
        interval.append(codepoint)
        combining.append(interval)
    return tuple(itertools.imap(tuple, combining))

# Handling of control chars rewritten.  Rest is JA's port of MK's C code.
# -Toshio Kuratomi
def _ucp_width(ucs, control_chars='guess'):
    '''Get the textual width of a ucs character.

    :arg ucs: integer representing a single unicode :term:`code point`
    :kwarg control_chars: specify how to deal with control chars.  Possible
        values are:
            :guess: (default) will take a guess for control code widths.  Most
                codes will return 0 width.  backspace, delete, and clear
                delete return -1.  escape currently returns -1 as well but
                this is not guaranteed as it's not always correct
            :strict: will raise
                :exc:`~kitchen.text.exceptions.ControlCharError` if
                a control code is encountered
    :raises ControlCharError: if the :term:`code point` is a unicode
        control character and :attr:`control_chars` is set to 'strict'
    :returns: :term:`textual width` of the character.

    .. note: It's important to remember this is :term:`textual width` and not
        the number of characters or bytes.
    '''
    # test for 8-bit control characters
    if ucs < 32 or (ucs >= 0x7f and ucs < 0xa0):
        # Control characted detected
        if control_chars == 'strict':
            raise ControlCharError(_('_ucp_width does not understand how to'
                ' assign a width value to control characters.'))
        if ucs in (0x08, 0x07F, 0x94):
            # Backspace, delete, and clear delete remove a single character
            return -1
        if ucs == 0x1b:
            # Excape is tricky.  It removes some number of characters that
            # come after it but the amount is dependent on what is
            # interpreting the code.
            # So this is going to often be wrong but other values will be
            # wrong as well.
            return -1
        # All other control characters get 0 width
        return 0

    if _interval_bisearch(ucs, _COMBINING):
        # Combining characters return 0 width as they will be combined with
        # the width from other characters
        return 0

    # if we arrive here, ucs is not a combining or C0/C1 control character

    return (1 + 
      (ucs >= 0x1100 and
       (ucs <= 0x115f or                     # Hangul Jamo init. consonants
        ucs == 0x2329 or ucs == 0x232a or
        (ucs >= 0x2e80 and ucs <= 0xa4cf and
         ucs != 0x303f) or                   # CJK ... Yi
        (ucs >= 0xac00 and ucs <= 0xd7a3) or # Hangul Syllables
        (ucs >= 0xf900 and ucs <= 0xfaff) or # CJK Compatibility Ideographs
        (ucs >= 0xfe10 and ucs <= 0xfe19) or # Vertical forms
        (ucs >= 0xfe30 and ucs <= 0xfe6f) or # CJK Compatibility Forms
        (ucs >= 0xff00 and ucs <= 0xff60) or # Fullwidth Forms
        (ucs >= 0xffe0 and ucs <= 0xffe6) or
        (ucs >= 0x20000 and ucs <= 0x2fffd) or
        (ucs >= 0x30000 and ucs <= 0x3fffd))))

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

# Wholly rewritten by me (LGPLv2+) -Toshio Kuratomi
def textual_width(msg, control_chars='guess', encoding='utf8', errors='replace'):
    '''Get the textual width of a string

    :arg msg: :class:`unicode` or byte :class:`str` to get the width of
    :kwarg control_chars: specify how to deal with control chars.  Possible
        values are:
            :guess: (default) will take a guess for control code widths.
            :strict: will raise
                a :exc:`~kitchen.text.exceptions.ControlCharError` if
                a control code is encountered
    :kwarg encoding: If we are given a byte :class:`str`, this is used to
        decode it into :class:`unicode`.  Any characters that are not
        decodable in this encoding will be assigned a width of 1.
    :kwarg errors: How to treat errors encoding the byte :class:`str` to
        :class:`unicode`.  Legal values are the same as for
        :func:`kitchen.text.converters.to_unicode`
    :raises ControlCharError: if :attr:`msg` contains a control character and
        control_chars is 'strict'.
    :returns: :term:`Textual width` of the :attr:`msg`.  This is the amount of
        space that the string will consume on a monospace display.  It's
        measured in the number of cell positions or columns it will take up on
        a monospace display.  This is **not** the number of glyphs that are in
        the string.

    .. note:: This function can be wrong sometimes because Unicode does not
        specify a strict width value for all of the :term:`code points`.  In
        particular, we've found that some Tamil characters take up to
        4 character cells but are represented with a lesser amount.
    '''
    # On python 2.6.4, x86_64, I've benchmarked a few alternate
    # implementations::
    #
    #   timeit.repeat('utf8.textual_width(data)', 'from __main__ import utf8, data',
    #       number=100)
    # I varied data by size and content (1MB of ascii, a few words, 43K utf8, unicode type
    #
    # :this implementation: fastest across the board
    #   
    # :list comprehension: 6-16% slower
    #   return sum([_ucp_width(ord(c), control_chars=control_chars) for c in msg])
    #
    # :generator expression: 9-18% slower
    #   return sum((_ucp_width(ord(c), control_chars=control_chars) for c in
    #           msg))
    #
    # :lambda: 10-19% slower
    #   return sum(itertools.imap(lambda x: _ucp_width(ord(x), control_chars),
    #           msg))
    #
    # :partial application: 13-22% slower
    #   func = functools.partial(_ucp_width, control_chars=control_chars)
    #   return sum(itertools.imap(func, itertools.imap(ord, msg)))
    #
    # :the original code: 4-38% slower
    #   The 4% was for the short, ascii only string.  All the other pieces of
    #   data yielded over 30% slower times.

    # Non decodable data is just assigned a single cell width
    msg = to_unicode(msg, encoding=encoding, errors=errors)
    # Add the width of each char
    return sum(
            # calculate width of each char
            itertools.starmap(_ucp_width,
                # Setup the arguments to _ucp_width
                itertools.izip(
                    # int value of each char
                    itertools.imap(ord, msg),
                    # control_chars arg in a form that izip will deal with
                    itertools.repeat(control_chars))))

# Wholly rewritten by me -Toshio Kuratomi
def textual_width_chop(msg, chop, encoding='utf8', errors='replace'):
    '''Given as string, return it chopped to a given :term:`textual width`

    :arg msg: :class:`unicode` or byte :class:`str` to chop
    :arg chop: Chop the string if it exceeds this :term:`textual width`
    :kwarg encoding: If we are given a byte :class:`str`, this is used to
        decode it into :class:`unicode`.  Any characters that are not
        decodable in this encoding will be assigned a width of 1.
    :kwarg errors: How to treat errors encoding the byte :class:`str` to
        :class:`unicode`.  Legal values are the same as for
        :func:`kitchen.text.converters.to_unicode`
    :rtype: :class:`unicode` string
    :returns: :class:`unicode` string of the :attr:`msg` chopped at the given
        :term:`textual width`

    This is what you want to use instead of %.*s, as it does the "right" thing
    with regard to :term:`UTF8` sequences, :term:`control character`s, and
    characters that take more than one cell position. Eg::

        >>> # Only displays 8 characters because it is operating on bytes
        >>> print "%.*s" % (10, 'café ñunru!')
        café ñun
        >>> # Properly operates on graphemes
        >>> '%s' % (textual_width_chop('café ñunru!', 10))
        café ñunru
        >>> # takes too many columns because the kanji need two cell positions
        >>> print '1234567890\n%.*s' % (10, u'一二三四五六七八九十')
        1234567890
        一二三四五六七八九十
        >>> # Properly chops at 10 columns
        >>> print '1234567890\n%s' % (textual_width_chop(u'一二三四五六七八九十', 10))
        1234567890
        一二三四五
    '''

    msg = to_unicode(msg, encoding=encoding, errors=errors)

    width = textual_width(msg)
    if width <= chop:
        return msg
    maximum = len(msg)
    if maximum > chop * 2:
        # A character can take at most 2 cell positions so this is the actual
        # maximum
        maximum = chop * 2
    minimum = 0
    eos = maximum
    if eos > chop:
        eos = chop
    width = textual_width(msg[:eos])

    while True:
        # if current width is high,
        if width > chop:
            # calculate new midpoint
            mid = minimum + (eos - minimum) / 2
            if mid == eos:
                break
            if (eos - chop) < (eos - mid):
                while width > chop:
                    width = width - _ucp_width(ord(msg[eos-1]))
                    eos -= 1
                return msg[:eos]
            # subtract distance between eos and mid from width
            width = width - textual_width(msg[mid:eos])
            maximum = eos
            eos = mid
        # if current width is low,
        elif width < chop:
            # calculate new midpoint
            mid = eos + (maximum - eos) / 2
            if mid == eos:
                break
            if (chop - eos) < (mid - eos):
                while width < chop:
                    new_width = _ucp_width(ord(msg[eos]))
                    width = width + new_width
                    eos += 1
                return msg[:eos]

            # add distance between eos and new mid to width
            width = width + textual_width(msg[eos:mid])
            minimum = eos
            eos = mid
            if eos > maximum:
                eos = maximum
                break
        # if current is just right
        else:
            return msg[:eos]
    return msg[:eos]

# I made some adjustments for using unicode but largely unchanged from JA's
# port of MK's code -Toshio
def textual_width_fill(msg, fill, chop=None, left=True, prefix='', suffix=''):
    '''Expand a unicode string to a specified "width" or chop to same.

    :arg msg: :class:`unicode` string to format
    :arg fill: pad string until the :term:`textual width` of the string is
        this length
    :kwarg chop: before doing anything else, chop the string to this length.
        Default: Don't chop the string at all
    :kwarg left: If True (default) left justify the string and put the padding
        on the right.  If False, pad on the left side.
    :kwarg prefix: Attach this string before the field we're filling
    :kwarg suffix: Append this string to the end of the field we're filling
    :rtype: :class:`unicode` string
    :returns: :attr:`msg`, formatted to fill the specified width.  If no
        :attr:`chop` is specified, the string could exceed the fill length
        when completed.  If :attr:`prefix` or :attr:`suffix` are printable
        characters, the string could be longer than fill width.

    .. warning:: :attr:`prefix` and :attr:`suffix` should be used for
        "invisible" characters, like highlighting, color changing escape
        codes, etc.  The fill characters are appended outside of any
        :attr:`prefix` or :attr:`suffix` elements.  This allows you to only
        highlight :attr:`msg` inside of the field you're filling.

    .. warning:: :attr:`msg`, :attr:`prefix`, and :attr:`suffix` should all be
        representable as unicode characters.  In particular, any escape
        sequences in :attr:`prefix` and :attr:`suffix` need to be convertible
        to :class:`unicode`.  If you need to use byte sequences here rather
        than unicode characters, use
        :func:`~kitchen.text.utf8.byte_string_textual_width_fill` instead.

    This function expands a string to fill a field of a particular width.  Use
    it instead of %*.*s, as it does the "right" thing with regard to
    :term:`UTF8` sequences, :term:`control character`s, and characters that
    take more than one cell position in a display.  Example usage::

        >>> msg = u'一二三四五六七八九十'
        >>> # This uses 10 characters instead of 10 cells:
        >>> u":%-*.*s:" % (10, 10, msg[:9])
        :一二三四五六七八九 :
        >>> # This uses 10 cells like we really want:
        >>> u":%s:" % (textual_width_fill(msg[:9], 10, 10))
        :一二三四五:

        >>> # Right aligned in the field
        >>> u"%20.10s" % (msg)
                  一二三四五六七八九十
        >>> u"%s" % (textual_width_fill(msg, 20, 10, left=False))
                  一二三四五

        >>> # Adding some escape characters to highlight the line
        >>> u"%s%20.10s%s" % (prefix, msg, suffix)
        u'\x1b[7m          一二三四五六七八九十\x1b[0m'
        >>> u"%s%s%s" % (prefix, utf8.textual_width_fill(msg, 20, 10, left=False), suffix)
        u'\x1b[7m          一二三四五\x1b[0m'

        >>> # If you don't want to highlight the fill as well
        >>> u"%s" % (utf8.textual_width_fill(msg, 20, 10, left=False, prefix=prefix, suffix=suffix))
        u'          \x1b[7m一二三四五\x1b[0m'
    '''
    msg = to_unicode(msg)
    if chop is not None:
        msg = textual_width_chop(msg, chop)
    width = textual_width(msg)
    if width >= fill:
        if prefix or suffix:
            msg = u''.join([prefix, msg, suffix])
    else:
        extra = u' ' * (fill - width)
        if left:
            msg = u''.join([prefix, msg, suffix, extra])
        else:
            msg = u''.join([extra, prefix, msg, suffix])
    return msg

def byte_string_textual_width_fill(msg, fill, chop=None, left=True, prefix='',
        suffix='', encoding='utf8', errors='replace'):
    '''Expand a byte :class:`str` to a specified "width" or chop to same.

    :arg msg: byte :class:`str` encoded in :term:`UTF8` that we want formatted
    :arg fill: pad :attr:`msg` until the :term:`textual width` is this long
    :kwarg chop: before doing anything else, chop the string to this length.
        Default: Don't chop the string at all
    :kwarg left: If True (default) left justify the string and put the padding
        on the right.  If False, pad on the left side.
    :kwarg prefix: Attach this byte :class:`str` before the field we're
        filling
    :kwarg suffix: Append this byte :class:`str` to the end of the field we're
        filling
    :rtype: byte :class:`str`
    :returns: :attr:`msg`, formatted to fill the specified width.  If no
        :attr:`chop` is specified, the string could exceed the fill length
        when completed.  If :attr:`prefix` or :attr:`suffix` are printable
        characters, the string could be longer than fill width.

    .. warning:: :attr:`prefix` and :attr:`suffix` should be used for
        "invisible" characters, like highlighting, color changing escape
        codes, etc.  The fill characters are appended outside of any
        :attr:`prefix` or :attr:`suffix` elements.  This allows you to only
        highlight :attr:`msg` inside of the field you're filling.

    .. seealso::
        :func:`~kitchen.text.utf8.textual_width_fill`
            For example usage.  This function has only two differences.

            1. it takes byte strings for :attr:`prefix` and :attr:`suffix` so
                you can pass in arbitrary sequences of bytes, not just unicode
                characters.
            2. it returns a byte :class:`str` instead of a :class:`unicode`
                string.
    '''
    prefix = to_bytes(prefix, encoding=encoding, errors=errors)
    suffix = to_bytes(suffix, encoding=encoding, errors=errors)

    if chop is not None:
        msg = textual_width_chop(msg, chop, encoding=encoding, errors=errors)
    width = textual_width(msg)
    msg = to_bytes(msg)

    if width >= fill:
        if prefix or suffix:
            msg = ''.join([prefix, msg, suffix])
    else:
        extra = ' ' * (fill - width)
        if left:
            msg = ''.join([prefix, msg, suffix, extra])
        else:
            msg = ''.join([extra, prefix, msg, suffix])

    return msg

def _textual_width_le(width, *args):
    '''Optimize the common case when deciding which textual width is larger

    :arg width: :term:`textual width` to compare against.
    :arg *args: :class:`unicode` strings to check the total :term:`textual
        width` of
    :returns: True if the total length of :attr:`args` are less than or equal
        to :attr:`width`.

    We often want to know "does X fit in Y".  It takes a while to use
    :func:`textual_width` to calculate this.  However, we know that the number
    of canonically composed :class:`unicode` characters is always going to
    have 1 or 2 for the textual_width per character.  With this we can take
    the following shortcuts:

    1) If the number of canonically composed characters is more than width,
       the true :term:`textual width` cannot be less than width.
    2) If the number of canonically composed characters * 2 is less than the
       width then the textual width must be ok.
    :term:`textual width` of a canonically composed :class:`unicode` string
    will always be greater than or equal to the the number of :class:`unicode`
    characters.  So we can first check if the number of composed
    :class:`unicode` characters is less than the asked for width.  If it is we
    can return True immediately.  If not, then we must do a full textual width
    lookup.
    '''
    chars = 0
    string = ''.join(args)
    string = unicodedata.normalize('NFC', string)
    if len(string) > width:
        return False
    elif len(string) * 2 <= width:
        return True
    elif len(to_bytes(string)) <= width:
        # Check against bytes.
        # utf8 has the property of having the same amount or more bytes per
        # character than textual width.
        return True
    else:
        true_width = textual_width(string)
    return true_width <= width

def wrap_lines(text, width=70, initial_indent='', subsequent_indent='',
        encoding='utf8', errors='replace'):
    '''Works like we want textwrap.wrap() to work, uses utf-8 data and
    doesn't screw up lists/blocks/etc.

    :arg text: string to wrap
    :kwarg width: width at which to wrap.  Default 70
    :kwarg initial_indent: string to use to indent the first line.  Default,
        do not indent.
    :kwarg subsequent_indent: string to use to wrap subsequent lines.  Default
        do not indent
    :returns: list of lines that have been text wrapped and indented.
    '''
    # Tested with:
    # yum info robodoc gpicview php-pear-Net-Socket wmctrl ustr moreutils
    #          mediawiki-HNP ocspd insight yum mousepad
    # ...at 120, 80 and 40 chars.
    # Also, notable among lots of others, searching for "\n  ":
    #   exim-clamav, jpackage-utils, tcldom, synaptics, "quake3",
    #   perl-Class-Container, ez-ipupdate, perl-Net-XMPP, "kipi-plugins",
    #   perl-Apache-DBI, netcdf, python-configobj, "translate-toolkit", alpine,
    #   "udunits", "conntrack-tools"
    #
    # Note that, we "fail" on:
    #   alsa-plugins-jack, setools*, dblatex, uisp, "perl-Getopt-GUI-Long",
    #   suitesparse, "synce-serial", writer2latex, xenwatch, ltsp-utils

    def _indent_at_beg(line):
        '''Return the indent to use for this and (possibly) subsequent lines

        :arg line: :class:`unicode` line of text to process
        :rtype: tuple
        :returns: tuple of count of whitespace before getting to the start of
            this line followed by a count to the following indent if this
            block of text is an entry in a list.
        '''
        # Find the first non-whitespace character
        try:
            char = line.strip()[0]
        except IndexError:
            # All whitespace
            return 0, 0
        else:
            count = line.find(char)

        # if we have a bullet character, check for list
        if char not in u'-*.o\u2022\u2023\u2218':
            # No bullet; not a list
            return count, 0

        # List: Keep searching until we hit the innermost list
        nxt = _indent_at_beg(line[count+1:])
        nxt = nxt[1] or nxt[0]
        if nxt:
            return count, count + 1 + nxt
        return count, 0

    initial_indent = to_unicode(initial_indent, encoding=encoding,
            errors=errors)
    subsequent_indent = to_unicode(subsequent_indent, encoding=encoding,
            errors=errors)
    subsequent_indent_width = textual_width(subsequent_indent)

    text = to_unicode(text, encoding=encoding, errors=errors).rstrip(u'\n')
    lines = text.expandtabs().split(u'\n')

    ret = []
    indent = initial_indent
    wrap_last = False
    cur_sab = 0
    cur_spc_indent = 0
    for line in lines:
        line = line.rstrip(u' ')
        (last_sab, last_spc_indent) = (cur_sab, cur_spc_indent)
        (cur_sab, cur_spc_indent) = _indent_at_beg(line)
        force_nl = False # We want to stop wrapping under "certain" conditions:
        if wrap_last and cur_spc_indent:      # if line starts a list or
            force_nl = True
        if wrap_last and cur_sab == len(line):# is empty line
            force_nl = True
        if wrap_last and not last_spc_indent:  # if line doesn't continue a list and
            if cur_sab >= 4 and cur_sab != last_sab: # is "block indented"
                force_nl = True
        if force_nl:
            ret.append(indent.rstrip(u' '))
            indent = subsequent_indent
            wrap_last = False
        if cur_sab == len(line): # empty line, remove spaces to make it easier.
            line = u''
        if wrap_last:
            line = line.lstrip(u' ')
            cur_spc_indent = last_spc_indent

        if _utf8_width_le(width, indent, line):
            wrap_last = False
            ret.append(indent + line)
            indent = subsequent_indent
            continue

        wrap_last = True
        words = line.split(u' ')
        line = indent
        spcs = cur_spc_indent
        if not spcs and cur_sab >= 4:
            spcs = cur_sab
        for word in words:
            if (not _textual_width_le(width, line, word) and
                textual_width(line) > subsequent_indent_width):
                ret.append(line.rstrip(u' '))
                line = subsequent_indent + u' ' * spcs
            line += word
            line += u' '
        indent = line.rstrip(u' ') + u' '
    if wrap_last:
        ret.append(indent.rstrip(u' '))

    return ret

def text_fill(text, *args, **kwargs):
    '''Works like we want textwrap.fill() to work, uses utf-8 data and
        doesn't screw up lists/blocks/etc.

    :arg text: string to process
    :returns: string with each line separated by a newline.

    .. seealso::
        :func:`utf8_text_wrap`
            for other parameters that you can give this command.

    This function is a light wrapper around :func:`utf8_text_wrap`.  Where
    that function returns a list of lines, this function returns one string
    with each line separated by a newline.
    '''
    return u'\n'.join(wrap_lines(text, *args, **kwargs))

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

    Use :func:`~kitchen.text.utf8.wrap_lines` instead
    '''
    warnings.warn(_('kitchen.text.utf8.utf8_text_wrap is deprecated.  Use'
        ' kitchen.text.utf8.wrap_lines instead'),
        DeprecationWarning, stacklevel=2)

    as_bytes = not isinstance(text, unicode)

    text = to_unicode(text)
    lines = wrap_lines(text, width=width, initial_indent=initial_indent,
            subsequent_indent=subsequent_indent)
    if as_bytes:
        lines = [to_bytes(m) for m in lines]

    return lines

def utf8_text_fill(text, *args, **kwargs):
    '''**Deprecated**  Use :func:`kitchen.text.utf8.text_fill` instead.'''
    warnings.warn(_('kitchen.text.utf8.utf8_text_fill is deprecated.  Use'
        ' kitchen.text.utf8.text_fill instead'),
        DeprecationWarning, stacklevel=2)
    # This assumes that all args. are utf8.
    return utf8_text_fill(text, *args, **kwargs)

def _utf8_width_le(width, *args):
    '''**Deprecated** Convert the arguments to unicode and use
    :func:`_textual_width_le` instead.
    '''
    warnings.warn(_('kitchen.text.utf8._utf8_width_le is deprecated.  Use'
        ' kitchen.text.utf8._textual_width_le instead'),
        DeprecationWarning, stacklevel=2)
    # This assumes that all args. are utf8.
    return _textual_width_le(width, to_unicode(''.join(args)))

__all__ = ('byte_string_textual_width_fill', 'textual_width',
        'textual_width_chop', 'textual_width_fill', 'utf8_text_fill',
        'utf8_text_wrap', 'utf8_valid', 'utf8_width', 'utf8_width_chop',
        'utf8_width_fill', 'wrap_lines')
