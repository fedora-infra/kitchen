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
# License along with python-fedora; if not, see <http://www.gnu.org/licenses/>
#
# Authors:
#   James Antill
#   Toshio Kuratomi <toshio@fedoraproject.org>
#   Seth Vidal
#
# Portions of this code taken from yum/misc.py and yum/i18n.py

import base64
import warnings
import xml.sax.saxutils

from kitchen import _
from kitchen.pycompat24 import builtinsets
from kitchen.text.exceptions import XmlEncodeError, ControlCharError
from kitchen.text.converters import guess_encoding, to_unicode, to_bytes

# ASCII control codes that are illegal in xml 1.0
_control_codes = frozenset(range(0, 8) + [11, 12] + range(14, 32))
_control_chars = frozenset(unichr(c) for c in _control_codes)

def unicode_to_xml(string, encoding='utf8', attrib=False,
        control_chars='replace'):
    '''Take a unicode string and turn it into a byte string suitable for xml

    :arg string: unicode string to encode for return
    :kwarg encoding: encoding to use for the returned byte string.  Default is
        to encode to utf8.  If all the characters in string are not encodable
        in this encoding, the unknown characters will be entered into the output
        string using xml character references.
    :kwarg attrib: If True, quote the string for use in an xml attribute.
        If False (default), quote for use in an xml text field.
    :kwarg control_chars: XML does not allow ASCII control characters.  When
        we encounter those we need to know what to do.  Valid options are:
        :replace: (default) Replace the control characters with "?"
        :ignore: Remove the characters altogether from the output
        :strict: Raise an error when we encounter a control character
    :raises XmlEncodeError: If control_chars is set to 'strict' and the string
        to be made suitable for output to xml contains control characters or if
        :attr:`string` is not a unicode type then we raise this exception.
    :raises ValueError: If control_chars is set o something other than
        replace, ignore, or strict.
    :rtype: byte string
    :returns: representation of the unicode string with any bytes that aren't
        available in xml taken care of.

    XML files consist mainly of text encoded using a particular charset.  XML
    also denies the use of certain bytes in the encoded text (example: ASCII
    Null).  There are also special characters that must be escaped if they are
    present in the input (example: "<").  This function takes care of all of
    those issues for you.

    There are a few different ways to use this function depending on your needs.
    The simplest invocation is like this::
       unicode_to_xml(u'String with non-ASCII characters: <"á と">')

    This will return the following to you, encoded in utf8::
      'String with non-ASCII characters: &lt;"á と"&gt;'

    Pretty straightforward.  Now, what if you need to encode your document in
    something other than utf8?  For instance, latin1?  Let's see::
       unicode_to_xml(u'String with non-ASCII characters: <"á と">', encoding='latin1')
       'String with non-ASCII characters: &lt;"á &#12392;"&gt;'

    Because the "と" character is not available in the latin1 charset, it is
    replaced with a "&#12392;" in our output.  This is an xml character
    reference which represents the character at unicode codepoint 12392, the
    "と" character.

    When you want to reverse this, use :func:`xml_to_unicode` which will turn
    a byte string to unicode and replace the xmlcharrefs with the unicode
    characters.

    XML also has the quirk of not allowing ASCII control characters in its
    output.  The control_chars parameter allows us to specify what to do with
    those.  For use cases that don't need absolute character by character
    fidelity (example: holding strings that will just be used for display
    in a GUI app later), the default value of 'replace' works well::
        unicode_to_xml(u'String with disallowed control chars: \u0000\u0007')
        'String with disallowed control chars: ??'

    If you do need to be able to reproduce all of the characters at a later
    date (examples: if the string is a key value in a database or a path on a
    filesystem) you have many choices.  Here are a few that rely on utf7, a
    verbose encoding that encodes control values (as well as all other unicode
    values) to characters from within the ASCII printable characters.  The good
    thing about doing this is that the code is pretty simple.  You just need to
    use utf7 both when encoding the field for xml and when decoding it for use
    in your python program::
        unicode_to_xml(u'String with unicode: と and control char: \u0007', encoding='utf7')
        'String with unicode: +MGg and control char: +AAc-'
        [...]
        xml_to_unicode('String with unicode: +MGg and control char: +AAc-', encoding='utf7')
        u'String with unicode: と and control char: \u0007'

    As you can see, the utf7 encoding will transform even characters that
    would be representable in utf8.  This can be a drawback if you want
    unicode characters in the file to be readable without being decoded first.
    You can work around this with increased complexity in your application
    code::
        encoding = 'utf8'
        u_string = u'String with unicode: と and control char: \u0007'
        try:
            # First attempt to encode to utf8
            data = unicode_to_xml(u_string, encoding=encoding, errors='strict')
        except XmlEncodeError:
            # Fallback to utf7
            encoding = 'utf7'
            data = unicode_to_xml(u_string, encoding=encoding, errors='strict')
        write_tag('<mytag encoding=%s>%s</mytag>' % (encoding, data))
        [...]
        encoding = tag.attributes.encoding
        u_string = xml_to_unicode(u_string, encoding=encoding)

    Using code similar to that, you can have some fields encoded using your
    default encoding and fallback to utf7 if there are control characters
    present.

    .. seealso::
        :func:`bytes_to_xml`
            if you're dealing with bytes that are non-text or of an unknown
            encoding that you must preserve on a byte for byte level.
        :func:`guess_encoding_to_xml`
            if you're dealing with strings in unknown encodings that you don't
            need to save with char-for-char fidelity.
    '''
    if not string:
        # Small optimization
        return ''
    try:
        process_control_chars(string, strategy=control_chars)
    except TypeError:
        raise XmlEncodeError(_('unicode_to_xml must have a unicode type as'
                ' the first argument.  Use bytes_string_to_xml for byte'
                ' strings.'))
    except ValueError:
        raise ValueError(_('The control_chars argument to unicode_to_xml'
                ' must be one of ignore, replace, or strict'))
    except ControlCharError, e:
        raise XmlEncodeError(e.args[0])

    string = string.encode(encoding, errors='xmlcharrefescape')

    # Escape characters that have special meaning in xml
    if attrib:
        string = xml.sax.saxutils.escape(string, entities={'"':"&quot;"})
    else:
        string = xml.sax.saxutils.escape(string)
    return string

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
import re
_ENTITY_RE = re.compile(r'(?s)<[^>]*>|&#?\w+;')

def html_entities_to_unicode(string):
    '''Substitute unicode characters for HTML entities

    :arg string: Unicode string to substitute out html entities

  @param text The HTML source.
  @return The plain text.  If the HTML source contains non-ASCII
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
            import htmlentitydefs
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
        return TypeError(_('html_entities_to_unicode must have a unicode type'
                ' for its first argument'))
    return re.sub(_ENTITY_RE, fixup, string)

def xml_to_unicode(byte_string, encoding, errors):
    string = to_unicode(byte_string, encoding=encoding, errors=errors)
    string = html_entities_to_unicode(string)
    return string

def xml_to_byte_string(byte_string, input_encoding, errors, output_encoding):
    string = xml_to_unicode(byte_string, input_encoding, errors)
    return to_bytes(string, output_encoding, errors)

def byte_string_to_xml(byte_string, input_encoding='utf8', errors='replace',
        output_encoding='utf8', attrib=False, control_chars='replace'):
    '''Make sure a byte string is validly encoded for xml output

    :arg byte_string: Byte string to make sure is valid xml output
    :kwarg input_encoding: Encoding of byte_string.  Default 'utf8'
    :kwarg errors: How to handle errors encountered while decoding the
        byte_string into unicode at the beginning of the process.  Values are:
        :replace: (default) Replace the invalid bytes with a '?'
        :ignore: Remove the characters altogether from the output
        :strict: Raise a UnicodeDecodeError when we encounter a non-decodable
            character
    :kwarg output_encoding: Encoding for the xml file that this string will go
        into.  Default is 'utf8'.  If all the characters in byte_string are
        not encodable in this encoding, the unknown characters will be
        entered into the output string using xml character references.
    :kwarg attrib: If True, quote the string for use in an xml attribute.
        If False (default), quote for use in an xml text field.
    :kwarg control_chars: XML does not allow ASCII control characters.  When
        we encounter those we need to know what to do.  Valid options are:
        :replace: (default) Replace the control characters with "?"
        :ignore: Remove the characters altogether from the output
        :strict: Raise an error when we encounter a control character
    :raises XmlEncodeError: If control_chars is set to 'strict' and the string
        to be made suitable for output to xml contains control characters then
        we raise this exception
    :raises UnicodeDecodeError: If errors is set to 'strict' and the
        byte_string contains bytes that are not decodable using input_encoding,
        this error is raised
    :rtype: byte string
    :returns: representation of the byte string in the output encoding with
        any bytes that aren't available in xml taken care of.

    Use this when you have a byte string representing text that you need
    to make suitable for output to xml.  There are several cases where this
    is the case.  For instance, if you need to transform some strings encoded
    in latin1 to utf8 for output::

        utf8_string = byte_string_to_xml(latin1_string, input_encoding='latin1')

    If you already have strings in the proper encoding you may still want to
    use this function to remove control characters::

        cleaned_string = byte_string_to_xml(string, input_encoding='utf8', output_encoding='utf8')

    .. seealso::

        :func:`unicode_to_xml`
            for other ideas on using this function
    '''
    if not isinstance(byte_string, str):
        raise XmlEncodeError(_('byte_string_to_xml can only take a byte'
                ' string as its first argument.  Use unicode_to_xml for'
                ' unicode strings'))

    # Decode the string into unicode
    u_string = unicode(byte_string, input_encoding, errors)
    return unicode_to_xml(u_string, encoding=output_encoding,
            attrib=attrib, control_chars=control_chars)

def bytes_to_xml(byte_string):
    '''Return a byte string encoded so it is valid inside of any xml file

    :arg byte_string: byte string to transform
    :rtype: byte string consisting of all ASCII characters
    :returns: byte string representation of the input.  This will be encoded
        using base64.

    This function is made especially to put binary information into xml
    documents.

    This function is intended for encoding things that must be preserved
    byte-for-byte.  If you want to encode a byte string that's text and don't
    mind losing the actual bytes you probably want to try byte_string_to_xml()
    or guess_bytes_to_xml().

    .. note:: Although the current implementation uses base64 and there's no
        plans to change it, that isn't guaranteed.  If you want to make sure
        that you can encode and decode these messages it's best to use
        :func:`xml_to_bytes` if you use this function to encode.
    '''
    # Can you do this yourself?  Yes, you can.
    return base64.b64encode(byte_string)

# Why do this?  Function calls in CPython are rather expensive.  We start by
# defining this as a function so we can get a docstring.  Then we redefine it
# as an attribute to save one useless function call.
bytes_to_xml = base64.b64encode

def xml_to_bytes(byte_string):
    '''Decode as string encoded using :func:`bytes_to_xml`

    :arg byte_string: byte string to transform.  This should be a base64
        encoded sequence of bytes originally generated by :func:`bytes_to_xml`.
    :rtype: byte string
    :returns: byte string that's the decoded input.

    If you've got fields in an xml document that were encoded with
    :func:`bytes_to_xml` then you want to use this function to undecode them.
    It converts a base64 encoded string into a byte string.
    '''
    return base64.b64decode(byte_string)

# Same note here as for bytes_to_xml
xml_to_bytes = base64.b64decode

def validate_byte_string(byte_string, encoding):
    '''Check that a byte string would be valid in xml

    :arg byte_string: Byte string to check
    :arg encoding: Encoding of the xml filename
    :returns: True if the string is valid, False if it would be invalid in the
        xml file

    In some cases you'll have a whole bunch of byte strings and rather than
    transforming them to unicode and back to byte strings for output to
    xml, you will just want to make sure they work with the xml file you're
    constructing.  This function will help you do that::

        ARRAY_OF_MOSTLY_UTF8_STRINGS = [...]
        processed_array = []
        for string in ARRAY_OF_MOSTLY_UTF8_STRINGS:
            if validate_byte_string(string, 'utf8'):
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

def guess_encoding_to_xml(string, output_encoding='utf8', attrib=False,
        control_chars='replace'):
    '''Return a byte string suitable for inclusion in xml

    :arg string: unicode or byte string to be transformed into a byte string
        suitable for inclusion in xml.  If string is a byte string we attempt
        to guess the encoding.  If we cannot guess, we fallback to latin1.
    :kwarg output_encoding: Output encoding for the byte string.  This should
        match the encoding of your xml file.
    :kwarg attrib: If True, escape the item for use in an attribute.  If False
         default) escape the item for use in a text node.
    :returns: utf8 encoded byte string

    '''
    # Unicode strings can just be run through unicode_to_xml()
    if isinstance(string, unicode):
        return unicode_to_xml(string, encoding=output_encoding,
                attrib=attrib, control_chars=control_chars)

    # Guess the encoding of the byte strings
    input_encoding = guess_encoding(string)

    # Return the new byte string
    return byte_string_to_xml(string, input_encoding=input_encoding,
            errors='replace', output_encoding=output_encoding,
            attrib=attrib, control_chars=control_chars)

def to_xml(string, encoding='utf8', attrib=False, control_chars='ignore'):
    '''Deprecated: Use guess_encoding_to_xml() instead
    '''
    warnings.warn(_('kitchen.text.converters.to_xml is deprecated.  Use'
            ' kitchen.text.converters.guess_encoding_to_xml instead.'),
            DeprecationWarning, stacklevel=2)
    return guess_encoding_to_xml(string, output_encoding=encoding,
            attrib=attrib, control_chars=control_chars)

__all__ = ('byte_string_to_xml', 'bytes_to_xml', 'guess_encoding_to_xml',
        'to_xml', 'unicode_to_xml', 'validate_byte_string')
