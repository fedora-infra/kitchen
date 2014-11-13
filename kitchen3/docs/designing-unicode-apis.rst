.. _DesigningUnicodeAwareAPIs:

============================
Designing Unicode Aware APIs
============================

APIs that deal with byte :class:`str` and :class:`unicode` strings are
difficult to get right.  Here are a few strategies with pros and cons of each.

.. contents::

-------------------------------------------------
Take either bytes or unicode, output only unicode
-------------------------------------------------

In this strategy, you allow the user to enter either :class:`unicode` strings
or byte :class:`str` but what you give back is always :class:`unicode`.  This
strategy is easy for novice endusers to start using immediately as they will
be able to feed either type of string into the function and get back a string
that they can use in other places.

However, it does lead to the novice writing code that functions correctly when
testing it with :term:`ASCII`-only data but fails when given data that contains
non-:term:`ASCII` characters.  Worse, if your API is not designed to be
flexible, the consumer of your code won't be able to easily correct those
problems once they find them.

Here's a good API that uses this strategy::

    from kitchen.text.converters import to_unicode

    def truncate(msg, max_length, encoding='utf8', errors='replace'):
        msg = to_unicode(msg, encoding, errors)
        return msg[:max_length]

The call to :func:`truncate` starts with the essential parameters for
performing the task.  It ends with two optional keyword arguments that define
the encoding to use to transform from a byte :class:`str` to :class:`unicode`
and the strategy to use if undecodable bytes are encountered.  The defaults
may vary depending on the use cases you have in mind.  When the output is
generally going to be printed for the user to see, ``errors='replace'`` is
a good default.  If you are constructing keys to a database, raisng an
exception (with ``errors='strict'``) may be a better default.  In either case,
having both parameters allows the person using your API to choose how they
want to handle any problems.  Having the values is also a clue to them that
a conversion from byte :class:`str` to :class:`unicode` string is going to
occur.

.. note::

    If you're targeting python-3.1 and above, ``errors='surrogateescape'`` may
    be a better default than ``errors='strict'``.  You need to be mindful of
    a few things when using ``surrogateescape`` though:

    * ``surrogateescape`` will cause issues if a non-:term:`ASCII` compatible
      encoding is used (for instance, UTF-16 and UTF-32.)  That makes it
      unhelpful in situations where a true general purpose method of encoding
      must be found.  :pep:`383` mentions that ``surrogateescape`` was
      specifically designed with the limitations of translating using system
      locales (where :term:`ASCII` compatibility is generally seen as
      inescapable) so you should keep that in mind.
    * If you use ``surrogateescape`` to decode from :class:`bytes`
      to :class:`unicode` you will need to use an error handler other than
      ``strict`` to encode as the lone surrogate that this error handler
      creates makes for invalid unicode that must be handled when encoding.
      In Python-3.1.2 or less, a bug in the encoder error handlers mean that
      you can only use ``surrogateescape`` to encode; anything else will throw
      an error.

    Evaluate your usages of the variables in question to see what makes sense.

Here's a bad example of using this strategy::

    from kitchen.text.converters import to_unicode

    def truncate(msg, max_length):
        msg = to_unicode(msg)
        return msg[:max_length]

In this example, we don't have the optional keyword arguments for
:attr:`encoding` and :attr:`errors`.  A user who uses this function is more
likely to miss the fact that a conversion from byte :class:`str` to
:class:`unicode` is going to occur.  And once an error is reported, they will
have to look through their backtrace and think harder about where they want to
transform their data into :class:`unicode` strings instead of having the
opportunity to control how the conversion takes place in the function itself.
Note that the user does have the ability to make this work by making the
transformation to unicode themselves::

    from kitchen.text.converters import to_unicode

    msg = to_unicode(msg, encoding='euc_jp', errors='ignore')
    new_msg = truncate(msg, 5)

--------------------------------------------------
Take either bytes or unicode, output the same type
--------------------------------------------------

This strategy is sometimes called polymorphic because the type of data that is
returned is dependent on the type of data that is received.  The concept is
that when you are given a byte :class:`str` to process, you return a byte
:class:`str` in your output.  When you are given :class:`unicode` strings to
process, you return :class:`unicode` strings in your output.

This can work well for end users as the ones that know about the difference
between the two string types will already have transformed the strings to
their desired type before giving it to this function.  The ones that don't can
remain blissfully ignorant (at least, as far as your function is concerned) as
the function does not change the type.

In cases where the encoding of the byte :class:`str` is known or can be
discovered based on the input data this works well.  If you can't figure out
the input encoding, however, this strategy can fail in any of the following
cases:

1. It needs to do an internal conversion between byte :class:`str` and
   :class:`unicode` string.
2. It cannot return the same data as either a :class:`unicode` string or byte
   :class:`str`.
3. You may need to deal with byte strings that are not byte-compatible with
   :term:`ASCII`

First, a couple examples of using this strategy in a good way::

    def translate(msg, table):
        replacements = table.keys()
        new_msg = []
        for index, char in enumerate(msg):
            if char in replacements:
                new_msg.append(table[char])
            else:
                new_msg.append(char)

        return ''.join(new_msg)

In this example, all of the strings that we use (except the empty string which
is okay because it doesn't have any characters to encode) come from outside of
the function.  Due to that, the user is responsible for making sure that the
:attr:`msg`, and the keys and values in :attr:`table` all match in terms of
type (:class:`unicode` vs :class:`str`) and encoding (You can do some error
checking to make sure the user gave all the same type but you can't do the
same for the user giving different encodings).  You do not need to make
changes to the string that require you to know the encoding or type of the
string; everything is a simple replacement of one element in the array of
characters in message with the character in table.

::

    import json
    from kitchen.text.converters import to_unicode, to_bytes

    def first_field_from_json_data(json_string):
        '''Return the first field in a json data structure.

        The format of the json data is a simple list of strings.
        '["one", "two", "three"]'
        '''
        if isinstance(json_string, unicode):
            # On all python versions, json.loads() returns unicode if given
            # a unicode string
            return json.loads(json_string)[0]

        # Byte str: figure out which encoding we're dealing with
        if '\x00' not in json_data[:2]
            encoding = 'utf8'
        elif '\x00\x00\x00' == json_data[:3]:
            encoding = 'utf-32-be'
        elif '\x00\x00\x00' == json_data[1:4]:
            encoding = 'utf-32-le'
        elif '\x00' == json_data[0] and '\x00' == json_data[2]:
            encoding = 'utf-16-be'
        else:
            encoding = 'utf-16-le'

        data = json.loads(unicode(json_string, encoding))
        return data[0].encode(encoding)

In this example the function takes either a byte :class:`str` type or
a :class:`unicode` string that has a list in json format and returns the first
field from it as the type of the input string.  The first section of code is
very straightforward; we receive a :class:`unicode` string, parse it with
a function, and then return the first field from our parsed data (which our
function returned to us as json data).

The second portion that deals with byte :class:`str` is not so
straightforward.  Before we can parse the string we have to determine what
characters the bytes in the string map to.  If we didn't do that, we wouldn't
be able to properly find which characters are present in the string.  In order
to do that we have to figure out the encoding of the byte :class:`str`.
Luckily, the json specification states that all strings are unicode and
encoded with one of UTF32be, UTF32le, UTF16be, UTF16le, or :term:`UTF-8`.  It further
defines the format such that the first two characters are always
:term:`ASCII`.  Each of these has a different sequence of NULLs when they
encode an :term:`ASCII` character.  We can use that to detect which encoding
was used to create the byte :class:`str`.

Finally, we return the byte :class:`str` by encoding the :class:`unicode` back
to a byte :class:`str`.

As you can see, in this example we have to convert from byte :class:`str` to
:class:`unicode` and back.  But we know from the json specification that byte
:class:`str` has to be one of a limited number of encodings that we are able
to detect.  That ability makes this strategy work.

Now for some examples of using this strategy in ways that fail::

    import unicodedata
    def first_char(msg):
        '''Return the first character in a string'''
        if not isinstance(msg, unicode):
            try:
                msg = unicode(msg, 'utf8')
            except UnicodeError:
                msg = unicode(msg, 'latin1')
        msg = unicodedata.normalize('NFC', msg)
        return msg[0]

If you look at that code and think that there's something fragile and prone to
breaking in the ``try: except:`` block you are correct in being suspicious.
This code will fail on multi-byte character sets that aren't :term:`UTF-8`.  It
can also fail on data where the sequence of bytes is valid :term:`UTF-8` but
the bytes are actually of a different encoding.  The reasons this code fails
is that we don't know what encoding the bytes are in and the code must convert
from a byte :class:`str` to a :class:`unicode` string in order to function.

In order to make this code robust we must know the encoding of :attr:`msg`.
The only way to know that is to ask the user so the API must do that::

    import unicodedata
    def number_of_chars(msg, encoding='utf8', errors='strict'):
        if not isinstance(msg, unicode):
            msg = unicode(msg, encoding, errors)
        msg = unicodedata.normalize('NFC', msg)
        return len(msg)

Another example of failure::

    import os
    def listdir(directory):
        files = os.listdir(directory)
        if isinstance(directory, str):
            return files
        # files could contain both bytes and unicode
        new_files = []
        for filename in files:
            if not isinstance(filename, unicode):
                # What to do here?
                continue
            new_files.appen(filename)
        return new_files

This function illustrates the second failure mode.  Here, not all of the
possible values can be represented as :class:`unicode` without knowing more
about the encoding of each of the filenames involved.  Since each filename
could have a different encoding there's a few different options to pursue.  We
could make this function always return byte :class:`str` since that can
accurately represent anything that could be returned.  If we want to return
:class:`unicode` we need to at least allow the user to specify what to do in
case of an error decoding the bytes to :class:`unicode`.  We can also let the
user specify the encoding to use for doing the decoding but that won't help in
all cases since not all files will be in the same encoding (or even
necessarily in any encoding)::

    import locale
    import os
    def listdir(directory, encoding=locale.getpreferredencoding(), errors='strict'):
        # Note: In python-3.1+, surrogateescape may be a better default
        files = os.listdir(directory)
        if isinstance(directory, str):
            return files
        new_files = []
        for filename in files:
            if not isinstance(filename, unicode):
                filename = unicode(filename, encoding=encoding, errors=errors)
            new_files.append(filename)
        return new_files

Note that although we use :attr:`errors` in this example as what to pass to
the codec that decodes to :class:`unicode` we could also have an
:attr:`errors` argument that decides other things to do like skip a filename
entirely, return a placeholder (``Nondisplayable filename``), or raise an
exception.

This leaves us with one last failure to describe::

    def first_field(csv_string):
        '''Return the first field in a comma separated values string.'''
        try:
            return csv_string[:csv_string.index(',')]
        except ValueError:
            return csv_string

This code looks simple enough.  The hidden error here is that we are searching
for a comma character in a byte :class:`str` but not all encodings will use
the same sequence of bytes to represent the comma.  If you use an encoding
that's not :term:`ASCII` compatible on the byte level, then the literal comma
``','`` in the above code will match inappropriate bytes.  Some examples of
how it can fail:

* Will find the byte representing an :term:`ASCII` comma in another character
* Will find the comma but leave trailing garbage bytes on the end of the
  string
* Will not match the character that represents the comma in this encoding

There are two ways to solve this.  You can either take the encoding value from
the user or you can take the separator value from the user.  Of the two,
taking the encoding is the better option for two reasons:

1. Taking a separator argument doesn't clearly document for the API user that
   the reason they must give it is to properly match the encoding of the
   :attr:`csv_string`.  They're just as likely to think that it's simply a way
   to specify an alternate character (like ":" or "|") for the separator.
2. It's possible for a variable width encoding to reuse the same byte sequence
   for different characters in multiple sequences.

   .. note::

        :term:`UTF-8` is resistant to this as any character's sequence of
        bytes will never be a subset of another character's sequence of bytes.

With that in mind, here's how to improve the API::

    def first_field(csv_string, encoding='utf-8', errors='replace'):
        if not isinstance(csv_string, unicode):
            u_string = unicode(csv_string, encoding, errors)
            is_unicode = False
        else:
            u_string = csv_string

        try:
            field = u_string[:U_string.index(u',')]
        except ValueError:
            return csv_string

        if not is_unicode:
            field = field.encode(encoding, errors)
        return field

.. note::

    If you decide you'll never encounter a variable width encoding that reuses
    byte sequences you can use this code instead::

        def first_field(csv_string, encoding='utf-8'):
            try:
                return csv_string[:csv_string.index(','.encode(encoding))]
            except ValueError:
                return csv_string

------------------
Separate functions
------------------

Sometimes you want to be able to take either byte :class:`str` or
:class:`unicode` strings, perform similar operations on either one and then
return data in the same format as was given.  Probably the easiest way to do
that is to have separate functions for each and adopt a naming convention to
show that one is for working with byte :class:`str` and the other is for
working with :class:`unicode` strings::

    def translate_b(msg, table):
        '''Replace values in str with other byte values like unicode.translate'''
        if not isinstance(msg, str):
            raise TypeError('msg must be of type str')
        str_table = [chr(s) for s in xrange(0,256)]
        delete_chars = []
        for chr_val in (k for k in table.keys() if isinstance(k, int)):
            if chr_val > 255:
                raise ValueError('Keys in table must not exceed 255)')
            if table[chr_val] == None:
                delete_chars.append(chr(chr_val))
            elif isinstance(table[chr_val], int):
                if table[chr_val] > 255:
                    raise TypeError('table values cannot be more than 255 or less than 0')
                str_table[chr_val] = chr(table[chr_val])
            else:
                if not isinstance(table[chr_val], str):
                    raise TypeError('character mapping must return integer, None or str')
                str_table[chr_val] = table[chr_val]
        str_table = ''.join(str_table)
        delete_chars = ''.join(delete_chars)
        return msg.translate(str_table, delete_chars)

    def translate(msg, table):
        '''Replace values in a unicode string with other values'''
        if not isinstance(msg, unicode):
            raise TypeError('msg must be of type unicode')
        return msg.translate(table)

There's several things that we have to do in this API:

* Because the function names might not be enough of a clue to the user of the
  functions of the value types that are expected, we have to check that the
  types are correct.

* We keep the behaviour of the two functions as close to the same as possible,
  just with byte :class:`str` and :class:`unicode` strings substituted for
  each other.


-----------------------------------------------------------------
Deciding whether to take str or unicode when no value is returned
-----------------------------------------------------------------

Not all functions have a return value.  Sometimes a function is there to
interact with something external to python, for instance, writing a file out
to disk or a method exists to update the internal state of a data structure.
One of the main questions with these APIs is whether to take byte
:class:`str`, :class:`unicode` string, or both.  The answer depends on your
use case but I'll give some examples here.

Writing to external data
========================

When your information is going to an external data source like writing to
a file you need to decide whether to take in :class:`unicode` strings or byte
:class:`str`.  Remember that most external data sources are not going to be
dealing with unicode directly.  Instead, they're going to be dealing with
a sequence of bytes that may be interpreted as unicode.  With that in mind,
you either need to have the user give you a byte :class:`str` or convert to
a byte :class:`str` inside the function.

Next you need to think about the type of data that you're receiving.  If it's
textual data, (for instance, this is a chat client and the user is typing
messages that they expect to be read by another person) it probably makes sense to
take in :class:`unicode` strings and do the conversion inside your function.
On the other hand, if this is a lower level function that's passing data into
a network socket, it probably should be taking byte :class:`str` instead.

Just as noted in the API notes above, you should specify an :attr:`encoding`
and :attr:`errors` argument if you need to transform from :class:`unicode`
string to byte :class:`str` and you are unable to guess the encoding from the
data itself.

Updating data structures
========================

Sometimes your API is just going to update a data structure and not
immediately output that data anywhere.  Just as when writing external data,
you should think about both what your function is going to do with the data
eventually and what the caller of your function is thinking that they're
giving you.  Most of the time, you'll want to take :class:`unicode` strings
and enter them into the data structure as :class:`unicode` when the data is
textual in nature.  You'll want to take byte :class:`str` and enter them into
the data structure as byte :class:`str` when the data is not text.  Use
a naming convention so the user knows what's expected.

-------------
APIs to Avoid
-------------

There are a few APIs that are just wrong.  If you catch yourself making an API
that does one of these things, change it before anyone sees your code.

Returning unicode unless a conversion fails
===========================================

This type of API usually deals with byte :class:`str` at some point and
converts it to :class:`unicode` because it's usually thought to be text.
However, there are times when the bytes fail to convert to a :class:`unicode`
string.  When that happens, this API returns the raw byte :class:`str` instead
of a :class:`unicode` string.  One example of this is present in the |stdlib|_:
python2's :func:`os.listdir`::

    >>> import os
    >>> import locale
    >>> locale.getpreferredencoding()
    'UTF-8'
    >>> os.mkdir('/tmp/mine')
    >>> os.chdir('/tmp/mine')
    >>> open('nonsense_char_\xff', 'w').close()
    >>> open('all_ascii', 'w').close()
    >>> os.listdir(u'.')
    [u'all_ascii', 'nonsense_char_\xff']

The problem with APIs like this is that they cause failures that are hard to
debug because they don't happen where the variables are set.  For instance,
let's say you take the filenames from :func:`os.listdir` and give it to this
function::

    def normalize_filename(filename):
        '''Change spaces and dashes into underscores'''
        return filename.translate({ord(u' '):u'_', ord(u' '):u'_'})

When you test this, you use filenames that all are decodable in your preferred
encoding and everything seems to work.  But when this code is run on a machine
that has filenames in multiple encodings the filenames returned by
:func:`os.listdir` suddenly include byte :class:`str`.  And byte :class:`str`
has a different :func:`string.translate` function that takes different values.
So the code raises an exception where it's not immediately obvious that
:func:`os.listdir` is at fault.

Ignoring values with no chance of recovery
==========================================

An early version of python3 attempted to fix the :func:`os.listdir` problem
pointed out in the last section by returning all values that were decodable to
:class:`unicode` and omitting the filenames that were not.  This lead to the
following output::

    >>> import os
    >>> import locale
    >>> locale.getpreferredencoding()
    'UTF-8'
    >>> os.mkdir('/tmp/mine')
    >>> os.chdir('/tmp/mine')
    >>> open(b'nonsense_char_\xff', 'w').close()
    >>> open('all_ascii', 'w').close()
    >>> os.listdir('.')
    ['all_ascii']

The issue with this type of code is that it is silently doing something
surprising.  The caller expects to get a full list of files back from
:func:`os.listdir`.  Instead, it silently ignores some of the files, returning
only a subset.  This leads to code that doesn't do what is expected that may
go unnoticed until the code is in production and someone notices that
something important is being missed.

Raising a UnicodeException with no chance of recovery
=====================================================

Believe it or not, a few libraries exist that make it impossible to deal
with unicode text without raising a :exc:`UnicodeError`.  What seems to occur
in these libraries is that the library has functions that expect to receive
a :class:`unicode` string.  However, internally, those functions call other
functions that expect to receive a byte :class:`str`.  The programmer of the
API was smart enough to convert from a :class:`unicode` string to a byte
:class:`str` but they did not give the user the chance to specify the
encodings to use or how to deal with errors.  This results in exceptions when
the user passes in a byte :class:`str` because the initial function wants
a :class:`unicode` string and exceptions when the user passes in
a :class:`unicode` string because the function can't convert the string to
bytes in the encoding that it's selected.

Do not put the user in the position of not being able to use your API without
raising a :exc:`UnicodeError` with certain values.  If you can only safely
take :class:`unicode` strings, document that byte :class:`str` is not allowed
and vice versa.  If you have to convert internally, make sure to give the
caller of your function parameters to control the encoding and how to treat
errors that may occur during the encoding/decoding process.  If your code will
raise a :exc:`UnicodeError` with non-:term:`ASCII` values no matter what, you
should probably rethink your API.

-----------------
Knowing your data
-----------------

If you've read all the way down to this section without skipping you've seen
several admonitions about the type of data you are processing affecting the
viability of the various API choices.

Here's a few things to consider in your data:

Do you need to operate on both bytes and unicode?
=================================================

Much of the data in libraries, programs, and the general environment outside
of python is written where strings are sequences of bytes.  So when we
interact with data that comes from outside of python or data that is about to
leave python it may make sense to only operate on the data as a byte
:class:`str`.  There's two times when this may make sense:

1. The user is intended to hand the data to the function and then the function
   takes care of sending the data outside of python (to the filesystem, over
   the network, etc).
2. The data is not representable as text.  For instance, writing a binary
   file format.

Even when your code is operating in this area you still need to think a little
more about your data.  For instance, it might make sense for the person using
your API to pass in :class:`unicode` strings and let the function convert that
into the byte :class:`str` that it then sends over the wire.

There are also times when it might make sense to operate only on
:class:`unicode` strings.  :class:`unicode` represents text so anytime that
you are working on textual data that isn't going to leave python it has the
potential to be a :class:`unicode`-only API.  However, there's two things that
you should consider when designing a :class:`unicode`-only API:

1. As your API gains popularity, people are going to use your API in places
   that you may not have thought of.  Corner cases in these other places may
   mean that processing bytes is desirable.
2. In python2, byte :class:`str` and :class:`unicode` are often used
   interchangably with each other.  That means that people programming against
   your API may have received :class:`str` from some other API and it would be
   most convenient for their code if your API accepted it.

.. note::

    In python3, the separation between the text type and the byte type
    are more clear.  So in python3, there's less need to have all APIs take
    both unicode and bytes.

Can you restrict the encodings?
===============================
If you determine that you have to deal with byte :class:`str` you should
realize that not all encodings are created equal.  Each has different
properties that may make it possible to provide a simpler API provided that
you can reasonably tell the users of your API that they cannot use certain
classes of encodings.

As one example, if you are required to find a comma (``,``) in a byte
:class:`str` you have different choices based on what encodings are allowed.
If you can reasonably restrict your API users to only giving :term:`ASCII
compatible` encodings you can do this simply by searching for the literal
comma character because that character will be represented by the same byte
sequence in all :term:`ASCII compatible` encodings.

The following are some classes of encodings to be aware of as you decide how
generic your code needs to be.

Single byte encodings
---------------------

Single byte encodings can only represent 256 total characters.  They encode
the :term:`code points` for a character to the equivalent number in a single
byte.

Most single byte encodings are :term:`ASCII compatible`.  :term:`ASCII
compatible` encodings are the most likely to be usable without changes to code
so this is good news.  A notable exception to this is the `EBDIC
<http://en.wikipedia.org/wiki/Extended_Binary_Coded_Decimal_Interchange_Code>`_
family of encodings.

Multibyte encodings
-------------------

Multibyte encodings use more than one byte to encode some characters.

Fixed width
~~~~~~~~~~~

Fixed width encodings have a set number of bytes to represent all of the
characters in the character set.  ``UTF-32`` is an example of a fixed width
encoding that uses four bytes per character and can express every unicode
characters.  There are a number of problems with writing APIs that need to
operate on fixed width, multibyte characters.  To go back to our earlier
example of finding a comma in a string, we have to realize that even in
``UTF-32`` where the :term:`code point` for :term:`ASCII` characters is the
same as in :term:`ASCII`, the byte sequence for them is different.  So you
cannot search for the literal byte character as it may pick up false
positives and may break a byte sequence in an odd place.

Variable Width
~~~~~~~~~~~~~~

ASCII compatible
""""""""""""""""

:term:`UTF-8` and the `EUC <http://en.wikipedia.org/wiki/Extended_Unix_Code>`_
family of encodings are examples of :term:`ASCII compatible` multi-byte
encodings.  They achieve this by adhering to two principles:

* All of the :term:`ASCII` characters are represented by the byte that they
  are in the :term:`ASCII` encoding.
* None of the :term:`ASCII` byte sequences are reused in any other byte
  sequence for a different character.

Escaped
"""""""

Some multibyte encodings work by using only bytes from the :term:`ASCII`
encoding but when a particular sequence of those byes is found, they are
interpreted as meaning something other than their :term:`ASCII` values.
``UTF-7`` is one such encoding that can encode all of the unicode
:term:`code points`.  For instance, here's a some Japanese characters encoded as
``UTF-7``::

    >>> a = u'\u304f\u3089\u3068\u307f'
    >>> print a
    くらとみ
    >>> print a.encode('utf-7')
    +ME8wiTBoMH8-

These encodings can be used when you need to encode unicode data that may
contain non-:term:`ASCII` characters for inclusion in an :term:`ASCII` only
transport medium or file.

However, they are not :term:`ASCII compatible` in the sense that we used
earlier as the bytes that represent a :term:`ASCII` character are being reused
as part of other characters.  If you were to search for a literal plus sign in
this encoded string, you would run across many false positives, for instance.

Other
"""""

There are many other popular variable width encodings, for instance ``UTF-16``
and ``shift-JIS``.  Many of these are not :term:`ASCII compatible` so you
cannot search for a literal :term:`ASCII` character without danger of false
positives or false negatives.
