========
Glossary
========

.. glossary::

    "Everything but the kitchen sink"
        An English idiom meaning to include nearly everything that you can
        think of.

    ASCII
        A character encoding that maps numbers to characters essential to
        American English.  It maps 128 characters using 7bits.

        .. seealso:: http://en.wikipedia.org/wiki/ASCII

    code point
        A number that maps to a particular abstract character.  Code points
        make it so that we have a number pointing to a character without
        worrying about implementation details of how those numbers are stored
        for the computer to read.  Encodings define how the code points map to
        particular sequences of bytes on disk  and in memory.

    control character
        The set of characters in unicode that are used, not to display glyphs
        o nthe screen, but to tell the displayin program to do something.

        aa seealso:: http://en.wikipedia.org/wiki/Control_character

    I18N
        I18N is an abbreviation for internationalization.  It's often used to
        signify the need to translate words, number and date formats, and
        other pieces of data in a computer program so that it will work well
        for people who speak another language than yourself.

    textual width
        The amount of horizontal space a character takes up on a monospaced
        screen.  The units are number of character cells or columns that it
        takes the place of.

    UTF8
        A character encoding that maps all unicode codepoints to a sequence of
        bytes.  It is compatible with :term:`ASCII`.  It uses a variable
        number of bytes to encode all of unicode.  ASCII characters take one
        byte.  Characters from other parts of unicode take two to four bytes.
        It is widespread as an encoding on the internet and in Linux.
