========
Glossary
========

.. glossary::

    "Everything but the kitchen sink"
        An English idiom meaning to include nearly everything that you can
        think of.

    API version
        Version that is meant for computer consumption.  This version is
        parsable and comparable by computers.  It contains information about
        a library's API so that computer software can decide whether it works
        with the software.

    ASCII
        A character encoding that maps numbers to characters essential to
        American English.  It maps 128 characters using 7bits.

        .. seealso:: http://en.wikipedia.org/wiki/ASCII

    ASCII compatible
        An encoding in which the particular byte that maps to a character in
        the :term:`ASCII` character set is only used to map to that character.
        This excludes EBDIC based encodings and many multi-byte fixed and
        variable width encodings since they reuse the bytes that make up the
        :term:`ASCII` encoding for other purposes.  :term:`UTF-8` is notable
        as a variable width encoding that is :term:`ASCII` compatible.

        .. seealso::

            http://en.wikipedia.org/wiki/Variable-width_encoding
                For another explanation of various ways bytes are mapped to
                characters in a possibly incompatible manner.

    code points
        :term:`code point`

    code point
        A number that maps to a particular abstract character.  Code points
        make it so that we have a number pointing to a character without
        worrying about implementation details of how those numbers are stored
        for the computer to read.  Encodings define how the code points map to
        particular sequences of bytes on disk  and in memory.

    control characters
        :term:`control character`

    control character
        The set of characters in unicode that are used, not to display glyphs
        on the screen, but to tell the display in program to do something.

        .. seealso:: http://en.wikipedia.org/wiki/Control_character

    grapheme
        characters or pieces of characters that you might write on a page to
        make words, sentences, or other pieces of text.

        .. seealso:: http://en.wikipedia.org/wiki/Grapheme

    I18N
        I18N is an abbreviation for internationalization.  It's often used to
        signify the need to translate words, number and date formats, and
        other pieces of data in a computer program so that it will work well
        for people who speak another language than yourself.

    message catalogs
        :term:`message catalog`

    message catalog
        Message catalogs contain translations for user-visible strings that
        are present in your code.  Normally, you need to mark the strings to
        be translated by wrapping them in one of several :mod:`gettext`
        functions.  The function serves two purposes:

        1. It allows automated tools to find which strings are supposed to be
           extracted for translation.
        2. The functions perform the translation when the program is running.

        .. seealso::
            `babel's documentation
            <http://babel.edgewall.org/wiki/Documentation/messages.html>`_
                for one method of extracting message catalogs from source
                code.

    Murphy's Law
        "Anything that can go wrong, will go wrong."

        .. seealso:: http://en.wikipedia.org/wiki/Murphy%27s_Law

    release version
        Version that is meant for human consumption.  This version is easy for
        a human to look at to decide how a particular version relates to other
        versions of the software.

    textual width
        The amount of horizontal space a character takes up on a monospaced
        screen.  The units are number of character cells or columns that it
        takes the place of.

    UTF-8
        A character encoding that maps all unicode :term:`code points` to a sequence
        of bytes.  It is compatible with :term:`ASCII`.  It uses a variable
        number of bytes to encode all of unicode.  ASCII characters take one
        byte.  Characters from other parts of unicode take two to four bytes.
        It is widespread as an encoding on the internet and in Linux.
