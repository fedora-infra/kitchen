-----------------------
Kitchen.text.converters
-----------------------

.. automodule:: kitchen.text.converters

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
:class:`unicode` type represents an abstract sequence of unicode text known as
:term:`code points`.  :class:`str`, on the other hand, really represents
a sequence of bytes.  Those bytes are converted by your operating system to
appear as characters on your screen using a particular encoding (usually
with a default defined by the operating system and customizable by the
individual user.) Although :term:`ASCII` characters are fairly standard in
what bytes represent each character, the bytes outside of the :term:`ASCII`
range are not.  In general, each encoding will map a different character to
a particular byte.  Newer encodings map individual characters to multiple
bytes (which the older encodings will instead treat as multiple characters).
In the face of these differences, python refuses to guess at an encoding and
instead issues a warning or exception and refuses to convert.

.. seealso::
    :ref:`overcoming-frustration`
        For a longer introduction on this subject.

Strategy for Explicit Conversion
================================

So what is the best method of dealing with this weltering babble of incoherent
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
a byte :class:`str`.  In general, anytime we're getting a value from outside
of python (The filesystem, reading data from the network, interacting with an
external command, reading values from the environment) we are interacting with
something that will want to give us a byte :class:`str`.  Some |stdlib|_
modules and third party libraries will automatically attempt to convert a byte
:class:`str` to :class:`unicode` strings for you.  This is both a boon and
a curse.  If the library can guess correctly about the encoding that the data
is in, it will return :class:`unicode` objects to you without you having to
convert.  However, if it can't guess correctly, you may end up with one of
several problems:

:exc:`UnicodeError`
    The library attempted to decode a byte :class:`str` into
    a :class:`unicode`, string failed, and raises an exception.
Garbled data
    If the library returns the data after decoding it with the wrong encoding,
    the characters you see in the :exc:`unicode` string won't be the ones that
    you expect.
A byte :class:`str` instead of :class:`unicode` string
    Some libraries will return a :class:`unicode` string when they're able to
    decode the data and a byte :class:`str`  when they can't.  This is
    generally the hardest problem to debug when it occurs.  Avoid it in your
    own code and try to avoid or open bugs against upstreams that do this. See
    :ref:`DesigningUnicodeAwareAPIs` for strategies to do this properly.

On line 8, we convert from a byte :class:`str` to a :class:`unicode` string.
:func:`~kitchen.text.converters.to_unicode` does this for us.  It has some
error handling and sane defaults that make this a nicer function to use than
calling :meth:`str.decode` directly:

* Instead of defaulting to the :term:`ASCII` encoding which fails with all
  but the simple American English characters, it defaults to :term:`UTF-8`.
* Instead of raising an error if it cannot decode a value, it will replace
  the value with the unicode "Replacement character" symbol (``�``).
* If you happen to call this method with something that is not a :class:`str`
  or :class:`unicode`, it will return an empty :class:`unicode` string.

All three of these can be overridden using different keyword arguments to the
function.  See the :func:`to_unicode` documentation for more information.

On line 15 we push the data back out to a file.  Two things you should note here:

1. We deal with the strings as :class:`unicode` until the last instant.  The
   string format that we're using is :class:`unicode` and the variable also
   holds :class:`unicode`.  People sometimes get into trouble when they mix
   a byte :class:`str` format with a variable that holds a :class:`unicode`
   string (or vice versa) at this stage.
2. :func:`~kitchen.text.converters.to_bytes`, does the reverse of
   :func:`to_unicode`.  In this case, we're using the default values which
   turn :class:`unicode` into a byte :class:`str` using :term:`UTF-8`.  Any
   errors are replaced with a ``�`` and sending nonstring objects yield empty
   :class:`unicode` strings.  Just like :func:`to_unicode`, you can look at
   the documentation for :func:`to_bytes` to find out how to override any of
   these defaults.

When to use an alternate strategy
---------------------------------

The default strategy of decoding to :class:`unicode` strings when you take
data in and encoding to a byte :class:`str` when you send the data back out
works great for most problems but there are a few times when you shouldn't:

* The values aren't meant to be read as text
* The values need to be byte-for-byte when you send them back out -- for
  instance if they are database keys or filenames.
* You are transferring the data between several libraries that all expect
  byte :class:`str`.

In each of these instances, there is a reason to keep around the byte
:class:`str` version of a value.  Here's a few hints to keep your sanity in
these situations:

1. Keep your :class:`unicode` and :class:`str` values separate.  Just like the
   pain caused when you have to use someone else's library that returns both
   :class:`unicode` and :class:`str` you can cause yourself pain if you have
   functions that can return both types or variables that could hold either
   type of value.
2. Name your variables so that you can tell whether you're storing byte
   :class:`str` or :class:`unicode` string.  One of the first things you end
   up having to do when debugging is determine what type of string you have in
   a variable and what type of string you are expecting.  Naming your
   variables consistently so that you can tell which type they are supposed to
   hold will save you from at least one of those steps.
3. When you get values initially, make sure that you're dealing with the type
   of value that you expect as you save it.  You can use :func:`isinstance`
   or :func:`to_bytes` since :func:`to_bytes` doesn't do any modifications of
   the string if it's already a :class:`str`.  When using :func:`to_bytes`
   for this purpose you might want to use::

        try:
            b_input = to_bytes(input_should_be_bytes_already, errors='strict', nonstring='strict')
        except:
            handle_errors_somehow()

   The reason is that the default of :func:`to_bytes` will take characters
   that are illegal in the chosen encoding and transform them to replacement
   characters.  Since the point of keeping this data as a byte :class:`str` is
   to keep the exact same bytes when you send it outside of your code,
   changing things to replacement characters should be rasing red flags that
   something is wrong.  Setting :attr:`errors` to ``strict`` will raise an
   exception which gives you an opportunity to fail gracefully.
4. Sometimes you will want to print out the values that you have in your byte
   :class:`str`.  When you do this you will need to make sure that you
   transform :class:`unicode` to :class:`str` before combining them.  Also be
   sure that any other function calls (including :mod:`gettext`) are going to
   give you strings that are the same type.  For instance::

        print to_bytes(_('Username: %(user)s'), 'utf-8') % {'user': b_username}

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
:class:`unicode`.  Sometimes it will return a byte :class:`str`.  Sometimes,
it will attempt to convert from a :class:`unicode` string to a byte
:class:`str`, fail, and throw a :exc:`UnicodeError`.  To be safe from all of
these, first decide whether you need :class:`unicode` or :class:`str` to be
returned.  Then use :func:`to_unicode` or :func:`to_bytes` to get the simple
representation like this::

    u_representation = to_unicode(obj, nonstring='simplerepr')
    b_representation = to_bytes(obj, nonstring='simplerepr')

print
-----

python has a builtin :func:`print` statement that outputs strings to the
terminal.  This originated in a time when python only dealt with byte
:class:`str`.  When :class:`unicode` strings came about, some enhancements
were made to the :func:`print` statement so that it could print those as well.
The enhancements make :func:`print` work most of the time.  However, the times
when it doesn't work tend to make for cryptic debugging.

The basic issue is that :func:`print` has to figure out what encoding to use
when it prints a :class:`unicode` string to the terminal.  When python is
attached to your terminal (ie, you're running the interpreter or running
a script that prints to the screen) python is able to take the encoding value
from your locale settings :envvar:`LC_ALL` or :envvar:`LC_CTYPE` and print the
characters allowed by that encoding.  On most modern Unix systems, the
encoding is :term:`utf-8` which means that you can print any :class:`unicode`
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
   terminal is run from an automated environment like :program:`cron`.  It
   also occurs when you have written a script using a :term:`utf-8` aware
   locale and released it for consumption by people all over the internet.
   Inevitably, someone is running with a locale that can't handle all unicode
   characters and you get a traceback reported.
2. You redirect output to a file.  Python isn't using the values in
   :envvar:`LC_ALL` unconditionally to decide what encoding to use.  Instead
   it is using the encoding set for the terminal you are printing to which is
   set to accept different encodings by :envvar:`LC_ALL`.  If you redirect
   to a file, you are no longer printing to the terminal so :envvar:`LC_ALL`
   won't have any effect.  At this point, python will decide it can't find an
   encoding and fallback to :term:`ASCII` which will likely lead to
   :exc:`UnicodeError` being raised.  You can see this in a short script::

        #! /usr/bin/python -tt
        print u'\ufffd'

   And then look at the difference between running it normally and redirecting to a file:

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

or you can wrap stdout and stderr with a :class:`~codecs.StreamWriter`.
A :class:`~codecs.StreamWriter` is convenient in that you can assign it to
encode for :data:`sys.stdout` or :data:`sys.stderr` and then have output
automatically converted but it has the drawback of still being able to throw
:exc:`UnicodeError` if the writer can't encode all possible unicode
codepoints.  Kitchen provides an alternate version which can be retrieved with
:func:`kitchen.text.converters.getwriter` which will not traceback in its
standard configuration.

.. _unicode-and-dict-keys:

Unicode, str, and dict keys
---------------------------

The :func:`hash` of the :term:`ASCII` characters is the same for
:class:`unicode` and byte :class:`str`.  When you use them in :class:`dict`
keys, they evaluate to the same dictionary slot::

    >>> u_string = u'a'
    >>> b_string = 'a'
    >>> hash(u_string), hash(b_string)
    (12416037344, 12416037344)
    >>> d = {}
    >>> d[u_string] = 'unicode'
    >>> d[b_string] = 'bytes'
    >>> d
    {u'a': 'bytes'}

When you deal with key values outside of :term:`ASCII`, :class:`unicode` and
byte :class:`str` evaluate unequally no matter what their character content or
hash value::

    >>> u_string = u'ñ'
    >>> b_string = u_string.encode('utf-8')
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
  :class:`unicode` or :class:`str`.  **Do not mix the two.**  If you're being
  given both :class:`unicode` and :class:`str` but you don't need to preserve
  separate keys for each, I recommend using :func:`to_unicode` or
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
  :class:`~kitchen.collections.strictdict.StrictDict` which has separate
  entries for all :class:`unicode` and byte :class:`str` and deals correctly
  with any :class:`tuple` containing mixed :class:`unicode` and byte
  :class:`str`.

---------
Functions
---------

Unicode and byte str conversion
===============================

.. autofunction:: kitchen.text.converters.to_unicode
.. autofunction:: kitchen.text.converters.to_bytes
.. autofunction:: kitchen.text.converters.getwriter
.. autofunction:: kitchen.text.converters.to_str
.. autofunction:: kitchen.text.converters.to_utf8

Transformation to XML
=====================

.. autofunction:: kitchen.text.converters.unicode_to_xml
.. autofunction:: kitchen.text.converters.xml_to_unicode
.. autofunction:: kitchen.text.converters.byte_string_to_xml
.. autofunction:: kitchen.text.converters.xml_to_byte_string
.. autofunction:: kitchen.text.converters.bytes_to_xml
.. autofunction:: kitchen.text.converters.xml_to_bytes
.. autofunction:: kitchen.text.converters.guess_encoding_to_xml
.. autofunction:: kitchen.text.converters.to_xml

Working with exception messages
===============================

.. autodata:: kitchen.text.converters.EXCEPTION_CONVERTERS
.. autodata:: kitchen.text.converters.BYTE_EXCEPTION_CONVERTERS
.. autofunction:: kitchen.text.converters.exception_to_unicode
.. autofunction:: kitchen.text.converters.exception_to_bytes
