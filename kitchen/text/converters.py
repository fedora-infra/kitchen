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
# License along with kitchen; if not, see <http://www.gnu.org/licenses/>
#
# Authors:
#   Toshio Kuratomi <toshio@fedoraproject.org>
#   Seth Vidal
#
# Portions of code taken from yum/i18n.py and
# python-fedora: fedora/textutils.py

'''
.. _kitchen.text.converters:

-----------------------
Kitchen.text.converters
-----------------------

Functions to handle conversion of byte strings and unicode strings.

Byte Strings and Unicode in Python2
===================================

Python2 has two string types, :class:`str` and :class:`unicode`.
:class:`unicode` represents an abstract sequence of text characters.  It can
hold any character that is present in the unicode standard.  :class:`str` can
hold any byte of data.  The operating system and python work together to
display these bytes as characters in many cases but you should always keep in
mind that the information is really a sequence of bytes, not a sequence of
characters.  In python2 these types are interchangeable a large amount of the
time.  They are one of the few pairs of types that automatically convert when
used in equality::

    >>> # string is converted to unicode and then compared
    >>> "I am a string" == u"I am a string"
    True
    >>> # Other types, like int, don't have this special treatment
    >>> 5 == "5"
    False

However, this automatic conversion tends to lull people into a false sense of
security.  As long as you're dealing with :term:`ASCII` characters the
automatic conversion will save you from seeing any differences.  Once you
start using characters that are not in :term:`ASCII`, you will start getting
:exc:`UnicodeError` and :exc:`UnicodeWarning` as the automatic conversions
between the types fail::

    >>> "I am an ñ" == u"I am an ñ"
    __main__:1: UnicodeWarning: Unicode equal comparison failed to convert both arguments to Unicode - interpreting them as being unequal
    False

Why do these conversions fail?  The reason is that the python2
:class:`unicode` represents an abstract sequence of text unicode codepoints.
:class:`str`, on the other hand, really represents a sequence of bytes.  Those
bytes are converted by your operating system to appear as characters on your
screen using a particular encoding (usually defined by the operating system
and customizable by the individual user.) Although :term:`ASCII` characters
are fairly standard in what bytes represent each character, the bytes outside
of the :term:`ASCII` range are not.  In general, each encoding will map
a different character to a particular byte.  The newer and better encodings
map individual characters to multiple bytes (which the older encodings will
instead treat as multiple characters).  In the face of these differences,
python refuses to guess at an encoding and instead issues a warning or
exception and refuses to convert.

Strategy for Explicit Conversion
================================

So what is the best method of dealing with this weltering babble on incoherent
encodings?  The basic strategy is to explicitly turn everything into
:class:`unicode` when it first enters your program.  Then, when you send it to
output, you can transform the unicode back into bytes.  Doing this allows you
to control the encodings that are used and avoid getting tracebacks due to
:exc:`UnicodeError`. Using the functions defined in this module, that looks
something like this:

.. code-block:: pycon
    :linenos:

    >>> from kitchen.text.converters import to_unicode, to_bytes
    >>> name = raw_input('Enter your name: ')
    Enter your name: Toshio くらとみ
    >>> name
    'Toshio \xe3\x81\x8f\xe3\x82\x89\xe3\x81\xa8\xe3\x81\xbf'
    >>> type(name)
    <type 'str'>
    >>> unicode_name = to_unicode(name)
    >>> type(unicode_name)
    <type 'unicode'>
    >>> unicode_name
    u'Toshio \u304f\u3089\u3068\u307f'
    >>> # Do a lot of other things before needing to save/output again:
    >>> output = open('datafile', 'w')
    >>> output.write(to_bytes(u'Name: %s\\n' % unicode_name))

A few notes:

Looking at line 6, you'll notice that the input we took from the user was
a :class:`str` (byte string).  In general, anytime we're getting a value from
outside of python (The filesystem, reading data from the network, interacting
with an external command, reading values from the environment) we are
interacting with something that will want to give us byte strings.  Some
libraries and python stdlib modules will automatically attempt to convert
those byte strings to unicode types for you.  This is both a boon and a curse.
If the library can guess correctly about the encoding that the data is in, it
will return :class:`unicode` objects to you without you having to convert.
However, if it can't guess correctly, you may end up with one of several
problems:

* A :exc:`UnicodeError`.  The library attempted to decode a byte string
    into :class:`unicode`, failed, and raises an error.
* Garbled data.  If the library returns the data after decoding it with the
    wrong encoding, the characters you see in the :exc:`unicode` string won't
    be the ones that you expect.
* You may get a byte string instead of unicode.  Some libraries will return
    :class:`unicode` when they're able to decode the data and bytes when they
    can't.  This is generally the hardest problem to debug when it occurs.
    Avoid it in your own code and try to avoid or open bugs against upstreams
    that do this.

On line 8, we convert from a :class:`str` to a :class:`unicode`.
:func:`~kitchen.text.converters.to_unicode` does this for us.  It has some
error handling and sane defaults that make this a nicer function to use than
calling :meth:`str.decode` directly:

* Instead of defaulting to the :term:`ASCII` encoding which fails with all
    but the simple American English characters, it defaults to :term:`UTF8`.
* Instead of raising an error if it cannot decode a value, it will replace
    the value with the unicode "Replacement character" symbol (�).
* If you happen to call this method with something that is not a :class:`str`
    or :class:`unicode`, it will return an empty unicode string.

All three of these can be overridden using different keyword arguments to the
function.  See the :func:`to_unicode` documentation for more information.

On line 15 we push the data back out to a file.  Two things you should note here:

1. We deal with the strings as :class:`unicode` until the last instant.  The
    string format that we're using is :class:`unicode` and the variable also
    holds :class:`unicode`.  People sometimes get into trouble when they mix
    a byte string format with a variable that holds unicode (or vice versa) at
    this stage.
2. :func:`~kitchen.text.converters.to_bytes`, does the reverse of
    :func:`to_unicode`.  In this case, we're using the default values which
    turn :class:`unicode` into a byte :class:`str` using :term:`UTF8`.  Any
    errors are replaced with a "?" and sending non-string objects yield empty
    :class:`unicode` strings.  Just like :func:`to_unicode`, you can look at
    the documentation for :func:`to_bytes` to find out how to override any of
    these defaults.

When to use an alternate strategy
---------------------------------

The default strategy of decoding to unicode types when you take data in and
encoding to bytes when you send the data back out works great for most
problems but there are a few times when you shouldn't:

* The values aren't meant to be read as text
* The values need to be byte-for-byte when you send them back out -- for
    instance if they are database keys or filenames.
* You are transferring the data between several libraries that all expect
    bytes.

In each of these instances, there is a reason to keep around the byte version
of a value.  Here's a few hints to keep your sanity in these situations:

1. Keep your :class:`unicode` and :class:`str` values separate.  Just like the
    pain caused when you have to use someone else's library that returns both
    :class:`unicode` and :class:`str` you can cause yourself pain if you have
    functions that can return both types or variables that could hold either
    type of value.
2. Name your variables so that you can tell whether you're storing byte
    :class:`str` or :class:`unicode`.  One of the first things you end up
    having to do when debugging is determine what type of string you have in a
    variable and what type of string you are expecting.  Naming your variables
    consistently so that you can tell which type they are supposed to hold
    will save you from at least one of those steps.
3. When you get values initially, make sure that you're dealing with the type
    of value that you expect as you save it.  You can use :func:`isinstance`
    or :func:`to_bytes` since :func:`to_bytes` doesn't do any modifications of
    the string if it's already a :class:`str`.  When using :func:`to_bytes`
    for this purpose you might want to use::

        try:
            b_input = to_bytes(input_should_be_bytes_already, errors='strict', non_string='strict')
        except:
            handle_errors_somehow()

    The reason is that the point of keeping this data as a byte :class:`str`
    is to keep the exact same bytes when you send it outside of your code.
    The default of :func:`to_bytes` will transform the input if it is not
    a :class:`str` so you want to be told that and have the opportunity to 
    fail gracefully.
4. Sometimes you will want to print out the values that you have in your byte
    strings.  When you do this you will need to make sure that you transform
    :class:`unicode` to :class:`str` before combining them.  Also be sure that
    any other function calls (including gettext) are going to give you strings
    that are the same type.  For instance::

        print to_bytes(_('Username: %(user)s'), 'utf8') % {'user': b_username}

Gotchas and how to avoid them
=============================

Even when you have a good conceptual understanding of how python2 treats
:class:`unicode` and :class:`str` there are still some things that can
surprise you.  In most cases this is because, as noted earlier, python or one
of the python libraries you depend on is trying to convert a value
automatically and failing.  Explicit conversion at the appropriate place
usually solves that.

str(obj)
--------

One common idiom for getting a simple, string representation of an object is to use::

    str(obj)

Unfortunately, this is not safe.  Sometimes str(obj) will return
:class:`unicode`, sometimes it will  return a byte :class:`str`.  Sometimes,
it will attempt to convert from a unicode string to a byte string, fail, and
throw a :exc:`UnicodeError`.  To be safe from all of these, first decide
whether you need :class:`unicode` or :class:`str` to be returned.  Then use
:func:`to_unicode` or :func:`to_bytes` to get the simple representation like
this::

    u_representation = to_unicode(obj, non_string='simplerepr')
    b_representation = to_bytes(obj, non_string='simplerepr')

print
-----

python has a builting ``print`` statement that outputs strings to the
terminal.  This originated in a time when python only dealt with byte
:class:`str`.  When :class:`unicode` strings came about, some enhancements
were made to the print statement so that it oculd print htose as well.  The
enhancements make print work most of the time however, the times when it
doesn't work tendto make for cryptic debugging.

The basic issue is that print has to figure out what encoding to use when it
prints a :class:`unicode` string to the terminal.  When python is attached to
your terminal (ie, you're running the interpreter or running a script that
prints to the screen) python is able to take the encoding value from your
locale settings :envvar:`LC_ALL` or :envvar:`LC_CTYPE` and print the
characters allowed by that encoding.  On most modern Unix systems, the
encoding is 'utf8' which means that you can print any :class:`unicode`
character without problem.

There are two common cases of things going wrong:

1. Someone has a locale set that does not accept all valid unicode characters.
    For instance::

        $ LC_ALL=C python
        >>> print u'\ufffd'
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        UnicodeEncodeError: 'ascii' codec can't encode character u'\ufffd' in position 0: ordinal not in range(128)

    This often happens when a script that you've written and debugged from the
    terminal is run from an automated environment like cron.  It also occurs
    when you have written a script using a utf-8 aware locale and released it
    for consumption by people all over the internet.  Inevitably, someone is
    running with a locale that can't handle all unicode characters and you get
    a traceback reported.
2. You redirect output to a file.  Python isn't using the values in
    :envvar:`LC_ALL` directly to decide what encoding to use.  Instead it is
    using the encoding set for the terminal you are printing to which is set
    to accept different encodings by the :envvar:`LC_ALL`.  If you redirect to
    a file, you are no longer printing to the termina so :envvar:`LC_ALL`
    won't have any effect.  At this point, python will decide it can't find an
    encoding and fallback to :term:`ASCII` which will likely lead to
    :exc:`UnicodeError` being raised.  You can see this in a short script::

        #! /usr/bin/python -tt
        print u'\ufffd'

    And then look at the difference between running it and redirecting to a terminal:

    .. code-block:: console

        $ ./test.py
        �
        $ ./test.py > t
        Traceback (most recent call last):
          File "test.py", line 3, in <module>
              print u'\ufffd'
        UnicodeEncodeError: 'ascii' codec can't encode character u'\ufffd' in position 0: ordinal not in range(128)

The short answer to dealing with this is to always use bytes when writing
output.  You can do this by explicitly converting to bytes like this::

    from kitchen.text.converters import to_bytes
    u_string = u'\ufffd'
    print to_bytes(u_string)

or you can wrap stdout and stderr with a :class:`codecs.StreamWriter`.
:class:`codecs.StreamWriter` is convenient in that you can assign it to encode
for stdout of stderr and then have output automatically converted but it has
the drawback of still being able to throw :exc:`UnicodeError` if the writer
can't encode all possible unicode codepoints.  See the `PrintFails
<http://wiki.python.org/moin/PrintFails>`_ page on the python.org wiki for
information on using this and a more in-depth analysis.

.. _unicode-and-dict-keys:

Unicode, str, and dict keys
---------------------------

The :func:`hash` of the :term:`ASCII` characters is the same for
:class:`unicode` and byte :class`str`.  When you use them in dictionary keys,
they evaluate to the same dictionary slot::

    >>> u_string = u'a'
    >>> b_string = 'a'
    >>> hash(u_string), hash(b_string)
    (12416037344, 12416037344)
    >>> d = {}
    >>> d[u_string] = 'unicode'
    >>> d[b_string] = 'bytes'
    >>> d
    {u'a': 'bytes'}

When you deal with key values outside of :TERM:`ASCII`, :class:`unicode` and
byte :class:`str` evaluate unequally no matter what their character content or
hash value::

    >>> u_string = u'ñ'
    >>> b_string = u_string.encode('utf8')
    >>> print u_string
    ñ
    >>> print b_string
    ñ
    >>> d = {}
    >>> d[u_string] = 'unicode'
    >>> d[b_string] = 'bytes'
    >>> d
    {u'\\xf1': 'unicode', '\\xc3\\xb1': 'bytes'}
    >>> b_string2 = '\\xf1'
    >>> hash(u_string), hash(b_string2)
    (30848092528, 30848092528)
    >>> d = {}
    >>> d[u_string] = 'unicode'
    >>> d[b_string2] = 'bytes'
    {u'\\xf1': 'unicode', '\\xf1': 'bytes'}

How do you work with this one?  Remember rule #1:  Keep your :class:`unicode`
and byte :class:`str` values separate.  That goes for keys in a dictionary
just like anything else.

* For any given dictionary, make sure that all your keys are either
    :class:`unicode` or :class:`str`.  *Do not mix the two.*  If you're being
    given both :class:`unicode` and :class:`str` but you don't need to
    preserve separate keys for each, I recommend using :func:`to_unicode` or
    :func:`to_bytes` to convert all keys to one type or the other like this::

        >>> from kitchen.text.converters import to_unicode
        >>> u_string = u'one'
        >>> b_string = 'two'
        >>> d = {}
        >>> d[to_unicode(u_string)] = 1
        >>> d[to_unicode(b_string)] = 2
        >>> d
        {u'two': 2, u'one': 1}

* These issues also apply to using dicts with tuple keys that contain
    a mixture of :class:`unicode` and :class:`str`.  Once again the best fix
    is to standardise on either :class:`str` or :class:`unicode`.

* If you absolutely need to store values in a dictionary where the keys could
    be either :class:`unicode` or :class:`str` you can use
    :class:`kitchen.collections.StrictDict` which has separate entries for all
    :class:`unicode` and byte :class:`str` and deals correctly with tuples
    containing mixed :class:`unicode` and byte :class:`str`.
'''
try:
    from base64 import b64encode, b64decode
except ImportError:
    from kitchen.pycompat24.base64modern import b64encode, b64decode

import warnings
import xml.sax.saxutils

from kitchen import _
from kitchen.text.exceptions import ControlCharError, XmlEncodeError
from kitchen.text.utils import guess_encoding, html_entities_unescape, \
        process_control_chars

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

        :empty: Return an empty string (default)
        :strict: Raise a TypeError
        :passthru: Return the object unchanged
        :simplerepr: Attempt to call the object's "simple representation"
            method and return that value.  Python-2.3+ has two methods
            that try to return a simple representation: __unicode__() and
            __str__().  We first try to get a usable value from
            __unicode__().  If that fails we try the same with __str__().
        :repr: Attempt to return a unicode string of the repr of the
            object

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

        :empty: Return an empty byte string (default)
        :strict: Raise a TypeError
        :passthru: Return the object unchanged
        :simplerepr: Attempt to call the object's "simple representation"
            method and return that value.  Python-2.3+ has two methods
            that try to return a simple representation: __unicode__() and
            __str__().  We first try to get a usable value from
            __str__().  If that fails we try the same with __unicode__().
        :repr: Attempt to return a byte string of the repr of the
            object

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
        try:
            obj_repr = obj.__repr__()
        except (AttributeError, UnicodeError):
            obj_repr = ''
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
        ' instead.  See the to_str docstring for'
        ' porting information.'),
        DeprecationWarning, stacklevel=2)
    return to_bytes(obj, non_string='simplerepr')

#
# XML Related Functions
#

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
    :raises ValueError: If control_chars is set to something other than
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

    string = string.encode(encoding, 'xmlcharrefreplace')

    # Escape characters that have special meaning in xml
    if attrib:
        string = xml.sax.saxutils.escape(string, entities={'"':"&quot;"})
    else:
        string = xml.sax.saxutils.escape(string)
    return string

def xml_to_unicode(byte_string, encoding='utf8', errors='replace'):
    '''Transform a byte string from an xml file into unicode

    :arg byte_string: byte string to decode
    :kwarg encoding: encoding that the byte string is in
    :kwarg errors: What to do if not every character is decodable using
        :attr:`encoding`.  See the :func:`to_unicode` docstring for
        legal values.
    :returns: unicode string decoded from :attr:`byte_string`

    This function attempts to reverse what :func:`unicode_to_xml` does.
    It takes a byte string (presumably read in from an xml file) and expands
    all the html entities into unicode characters and decodes the bytes into
    a unicode string.  One thing it cannot do is restore any control
    characters that were removed prior to inserting into the file.  If you
    need to keep such characters you need to use func:`xml_to_bytes` and
    :func:`bytes_to_xml` instead.
    '''
    string = to_unicode(byte_string, encoding=encoding, errors=errors)
    string = html_entities_unescape(string)
    return string

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
        we raise this exception.
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

def xml_to_byte_string(byte_string, input_encoding='utf8', errors='replace', output_encoding='utf8'):
    '''Transform a byte string from an xml file into unicode

    :arg byte_string: byte string to decode
    :kwarg input_encoding: encoding that the byte string is in
    :kwarg errors: What to do if not every character is decodable using
        :attr:`encoding`.  See the :func:`to_unicode` docstring for
        legal values.
    :kwarg output_encoding: Encoding for the output byte string
    :returns: unicode string decoded from :attr:`byte_string`

    This function attempts to reverse what :func:`unicode_to_xml` does.
    It takes a byte string (presumably read in from an xml file) and expands
    all the html entities into unicode characters and decodes the bytes into
    a unicode string.  One thing it cannot do is restore any control
    characters that were removed prior to inserting into the file.  If you
    need to keep such characters you need to use func:`xml_to_bytes` and
    :func:`bytes_to_xml` instead.
    '''
    string = xml_to_unicode(byte_string, input_encoding, errors)
    return to_bytes(string, output_encoding, errors)

def bytes_to_xml(byte_string, *args, **kwargs):
    '''Return a byte string encoded so it is valid inside of any xml file

    :arg byte_string: byte string to transform
    :arg *args, **kwargs: extra arguments to this function are passed on to the
        function actually implementing the encoding.  You can use this to tweak
        the output in some cases but, as a general rule, you shouldn't because
        the underlying encoding function is not guaranteed to remain the same.
    :rtype: byte string consisting of all ASCII characters
    :returns: byte string representation of the input.  This will be encoded
        using base64.

    This function is made especially to put binary information into xml
    documents.

    This function is intended for encoding things that must be preserved
    byte-for-byte.  If you want to encode a byte string that's text and don't
    mind losing the actual bytes you probably want to try byte_string_to_xml()
    or guess_bytes_to_xml().

    .. note:: Although the current implementation uses base64.b64encode and
        there's no plans to change it, that isn't guaranteed.  If you want to
        make sure that you can encode and decode these messages it's best to
        use :func:`xml_to_bytes` if you use this function to encode.
    '''
    # Can you do this yourself?  Yes, you can.
    return b64encode(byte_string, *args, **kwargs)

# Why do this?  Function calls in CPython are rather expensive.  We start by
# defining this as a function so we can get a docstring.  Then we redefine it
# as an attribute to save one useless function call.
bytes_to_xml = b64encode

def xml_to_bytes(byte_string, *args, **kwargs):
    '''Decode as string encoded using :func:`bytes_to_xml`

    :arg byte_string: byte string to transform.  This should be a base64
        encoded sequence of bytes originally generated by :func:`bytes_to_xml`.
    :arg *args, **kwargs: extra arguments to this function are passed on to the
        function actually implementing the encoding.  You can use this to tweak
        the output in some cases but, as a general rule, you shouldn't because
        the underlying encoding function is not guaranteed to remain the same.
    :rtype: byte string
    :returns: byte string that's the decoded input.

    If you've got fields in an xml document that were encoded with
    :func:`bytes_to_xml` then you want to use this function to undecode them.
    It converts a base64 encoded string into a byte string.

    .. note:: Although the current implementation uses base64.b64decode and
        there's no plans to change it, that isn't guaranteed.  If you want to
        make sure that you can encode and decode these messages it's best to
        use :func:`bytes_to_xml` if you use this function to decode.
    '''
    return b64decode(byte_string, *args, **kwargs)

# Same note here as for bytes_to_xml
xml_to_bytes = b64decode

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
        'to_bytes', 'to_str', 'to_unicode', 'to_utf8', 'to_xml',
        'unicode_to_xml', 'xml_to_byte_string', 'xml_to_bytes',
        'xml_to_unicode')
