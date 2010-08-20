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

The call to :func:`truncate` start with the essential parameters for
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

Here's a few bad APIs that uses this strategy::

    from kitchen.text.converters import to_unicode

    def truncate(msg, max_length):
        msg = to_unicode(msg)
        return msg[:max_length]

In this example, we don't have the optional keyword arguments for
:attr:`encoding` and :attr:`errors`.  A user who uses this function is more
likely to miss the fact that a conversion from byte :class:`str` to
:class:`unicode` is going to occur.  And once an error is reported, they will
have to look through their backtrace and think harder about where they want to
transform their data into :class:`unicode` strings.  Note that the user does have the
ability to make this work by making the transformation to unicode themselves::

    from kitchen.text.converters import to_unicode

    msg = to_unicode(msg, encoding='euc_jp', errors='ignore')
    new_msg = truncate(msg, 5)

------------------
Separate functions
------------------

Sometimes you want to be able to take either byte :class:`str` or
:class:`unicode` strings, perform similar operations on either one and then
return data in the same format as was given.  Probably the easiest way to do
that is to have separate functions for each and adopt a naming convention to
show that one is for working with byte :class:`str` and the other is for
working with :class:`unicode` strings.

    def translateb(msg, table):
        pass

-----------------------------------------------------
Take either bytes or unicode, output bytes or unicode
-----------------------------------------------------

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
hte input encoding, however, this strategy will fail in any of the following
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
msg, keys, and values in table all match in terms of type (:class:`unicode` vs
:class:`str`) and encoding (You can do some error checking to error if the
user doesn't give all the same type.  You can't do the same for the user
giving different encodings).  You do not need to make changes to the 
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

This function takes either a byte :class:`str` type or a :class:`unicode`
string that has a list in json format and returns the first field from it as
the type of the input string.  The first section of code is very
straightforward; we receive a :class:`unicode` string, parse it with
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
            if not isinstance(filename, unicode)
                # What to do here?
                continue
            new_files.appen(filename)
        return new_files

This function illustrates the second failure mode.  Here, not all of the
possible values can be represented as :class:`unicode` without knowing more
about the encoding of each of the filenames involved.  Since each filename
could have a different encoding what we probably need most is to know what to
do when we encounter an error::

    import locale
    import os
    def listdir(directory, errors='strict'):
        # Note: In python-3.1+, surrogateescape may be a better default
        files = os.listdir(directory)
        if isinstance(directory, str):
            return files
        new_files = []
        for filename in files:
            if not isinstance(filename, unicode):
                if errors == 'ignore':
                    continue
                filename = unicode(filename, encoding=locale.getpreferredencoding(), errors=errors)
            new_files.append(filename)
        return new_files

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
        :term:`UTF-8` is resistant to this character's sequence of bytes will
        ever be a subset of another character's sequence of bytes.

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
            field = field.decode(encoding, errors)
        return field

.. note:: If you decide you'll never encounter a variable width encoding that
    reuses byte sequences you can use this code instead::

        def first_field(csv_string, encoding='utf-8'):
            try:
                return csv_string[:csv_string.index(','.encode(encoding))]
            except ValueError:
                return csv_string

-------------
APIs to Avoid
-------------

There are a few APIs that are just wrong.  If you catch yourself making an API
that does one of these things, change it before anyone sees your code.

Returning unicode unless a conversion fails
===========================================

One example of this is present in the |stdlib|: :func:`os.listdir`::

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
