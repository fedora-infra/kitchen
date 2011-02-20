# -*- coding: utf-8 -*-
#
# Copyright (c) 2010 Red Hat, Inc
# Copyright (c) 2009 Milos Komarcevic
# Copyright (c) 2008 Tim Lauridsen
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
# Authors: James Antill
#   Milos Komarcevic
#   Toshio Kuratomi <toshio@fedoraproject.org>
#   Tim Lauridsen
#   Luke Macken <lmacken@redhat.com>
#   Seth Vidal <skvidal@fedoraproject.org>
#
# Portions of code taken from yum/i18n.py
'''
:term:`I18N` is an important piece of any modern program.  Unfortunately,
setting up :term:`i18n` in your program is often a confusing process.  The
functions provided here aim to make the programming side of that a little
easier.

Most projects will be able to do something like this when they startup::

    # myprogram/__init__.py:

    import os
    import sys

    from kitchen.i18n import easy_gettext_setup

    _, N_  = easy_gettext_setup('myprogram', localedirs=(
            os.path.join(os.path.realpath(os.path.dirname(__file__)), 'locale'),
            os.path.join(sys.prefix, 'lib', 'locale')
            ))

Then, in other files that have strings that need translating::

    # myprogram/commands.py:

    from myprogram import _, N_

    def print_usage():
        print _(u"""available commands are:
        --help              Display help
        --version           Display version of this program
        --bake-me-a-cake    as fast as you can
            """)

    def print_invitations(age):
        print _('Please come to my party.')
        print N_('I will be turning %(age)s year old',
            'I will be turning %(age)s years old', age) % {'age': age}

See the documentation of :func:`easy_gettext_setup` and
:func:`get_translation_object` for more details.

    .. seealso::

        :mod:`gettext`
            for details of how the python gettext facilities work
        `babel <http://babel.edgewall.org>`_
            The babel module for in depth information on gettext, :term:`message
            catalogs`, and translating your app.  babel provides some nice
            features for :term:`i18n` on top of :mod:`gettext`
'''
# Pylint disabled messages:
# :E1101: NewGNUTranslations is modeled as a replacement for GNUTranslations.
#   That module invokes the _parse message to create some of its attributes.
#   Pylint doesn't see those attributes being defined since it doesn't know
#   when _parse() is called.  We disable E1101 when accessing self._catalog
#   and self.plural for this reason.
# :C0103: We're replicating the gettext API here so we need to use method and
#   parameter names that mirror gettext.
# :C0111: We're replicating the gettext API here so for the gettext
#   translation object methods we point people at the stdlib docs

from kitchen.versioning import version_tuple_to_string

__version_info__ = ((2, 0, 0),)
__version__ = version_tuple_to_string(__version_info__)

import gettext
import locale
import os
import sys

from kitchen.text.converters import to_bytes, to_unicode

class DummyTranslations(gettext.NullTranslations):
    '''Safer version of :class:`gettext.NullTranslations`

    This Translations class doesn't translate the strings and is intended to
    be used as a fallback when there were errors setting up a real
    Translations object.  It's safer than :class:`gettext.NullTranslations` in
    its handling of byte :class:`str` vs :class:`unicode` strings.

    Unlike :class:`~gettext.NullTranslations`, this Translation class will
    never throw a :exc:`~exceptions.UnicodeError`.  The code that you have
    around a call to :class:`DummyTranslations` might throw
    a :exc:`~exceptions.UnicodeError` but at least that will be in code you
    control and can fix.  Also, unlike :class:`~gettext.NullTranslations` all
    of this Translation object's methods guarantee to return byte :class:`str`
    except for :meth:`ugettext` and :meth:`ungettext` which guarantee to
    return :class:`unicode` strings.

    When byte :class:`str` are returned, the strings will be encoded according
    to this algorithm:

    1) If a fallback has been added, the fallback will be called first.
       You'll need to consult the fallback to see whether it performs any
       encoding changes.
    2) If a byte :class:`str` was given, the same byte :class:`str` will
       be returned.
    3) If a :class:`unicode` string was given and :meth:`set_output_charset`
       has been called then we encode the string using the
       :attr:`output_charset`
    4) If a :class:`unicode` string was given and this is :meth:`gettext` or
       :meth:`ngettext` and :attr:`_charset` was set output in that charset.
    5) If a :class:`unicode` string was given and this is :meth:`gettext`
       or :meth:`ngettext` we encode it using 'utf-8'.
    6) If a :class:`unicode` string was given and this is :meth:`lgettext`
       or :meth:`lngettext` we encode using the value of
       :func:`locale.getpreferredencoding`

    For :meth:`ugettext` and :meth:`ungettext`, we go through the same set of
    steps with the following differences:

    * We transform byte :class:`str` into :class:`unicode` strings for
      these methods.
    * The encoding used to decode the byte :class:`str` is taken from
      :attr:`input_charset` if it's set, otherwise we decode using
      :term:`UTF-8`.

    .. attribute:: input_charset
    
        is an extension to the |stdlib|_ :mod:`gettext` that specifies what
        charset a message is encoded in when decoding a message to
        :class:`unicode`.  This is used for two purposes:

    1) If the message string is a byte :class:`str`, this is used to decode
       the string to a :class:`unicode` string before looking it up in the
       :term:`message catalog`.
    2) In :meth:`~kitchen.i18n.DummyTranslations.ugettext` and
       :meth:`~kitchen.i18n.DummyTranslations.ungettext` methods, if a byte
       :class:`str` is given as the message and is untranslated this is used
       as the encoding when decoding to :class:`unicode`.  This is different
       from :attr:`_charset` which may be set when a :term:`message catalog`
       is loaded because :attr:`input_charset` is used to describe an encoding
       used in a python source file while :attr:`_charset` describes the
       encoding used in the :term:`message catalog` file.

    Any characters that aren't able to be transformed from a byte :class:`str`
    to :class:`unicode` string or vice versa will be replaced with
    a replacement character (ie: ``u'�'`` in unicode based encodings, ``'?'`` in other
    :term:`ASCII` compatible encodings).

    .. seealso::
        :class:`gettext.NullTranslations`
            For information about what methods are available and what they do.

    '''
    #pylint: disable-msg=C0103,C0111
    def __init__(self, fp=None):
        gettext.NullTranslations.__init__(self, fp)

        # Python 2.3 compat
        if not hasattr(self, '_output_charset'):
            self._output_charset = None
        if not hasattr(self, 'output_charset'):
            self.output_charset = self.__output_charset
        if not hasattr(self, 'set_output_charset'):
            self.set_output_charset = self.__set_output_charset

        # Extension for making ugettext and ungettext more sane
        # 'utf-8' is only a default here.  Users can override.
        self.input_charset = 'utf-8'

    def __set_output_charset(self, charset):
        ''' Compatibility for python2.3 which doesn't have output_charset'''
        self._output_charset = charset

    def __output_charset(self):
        '''Compatibility for python2.3 which doesn't have output_charset'''
        return self._output_charset

    def gettext(self, message):
        if not isinstance(message, basestring):
            return ''
        if self._fallback:
            msg = to_unicode(message, encoding=self.input_charset)
            try:
                message = self._fallback.gettext(msg)
            except UnicodeError:
                # Ignore UnicodeErrors: We'll do our own encoding next
                pass

        # Make sure that we're returning a str
        if self._output_charset:
            return to_bytes(message, encoding=self._output_charset)
        elif self._charset:
            return to_bytes(message, encoding=self._charset)
        return to_bytes(message)

    def ngettext(self, msgid1, msgid2, n):
        # Default
        if n == 1:
            message = msgid1
        else:
            message = msgid2
        # The fallback method might return something different
        if self._fallback:
            msgid1 = to_unicode(msgid1, encoding=self.input_charset)
            msgid2 = to_unicode(msgid2, encoding=self.input_charset)
            try:
                message = self._fallback.ngettext(msgid1, msgid2, n)
            except UnicodeError:
                # Ignore UnicodeErrors: We'll do our own encoding next
                pass

        # Make sure that we're returning a str
        if self._output_charset:
            return to_bytes(message, encoding=self._output_charset,
                    nonstring='empty')
        elif self._charset:
            return to_bytes(message, encoding=self._charset,
                    nonstring='empty')
        return to_bytes(message, nonstring='empty')

    def lgettext(self, message):
        if not isinstance(message, basestring):
            return ''
        if self._fallback:
            msg = to_unicode(message, encoding=self.input_charset)
            try:
                message = self._fallback.lgettext(msg)
            except (AttributeError, UnicodeError):
                # Ignore UnicodeErrors: we'll do our own encoding next
                # AttributeErrors happen on py2.3 where lgettext is not
                # implemented
                pass

        # Make sure that we're returning a str
        if self._output_charset:
            return to_bytes(message, encoding=self._output_charset)
        return to_bytes(message, encoding=locale.getpreferredencoding())

    def lngettext(self, msgid1, msgid2, n):
        # Default
        if n == 1:
            message = msgid1
        else:
            message = msgid2
        # Fallback method might have something different
        if self._fallback:
            msgid1 = to_unicode(msgid1, encoding=self.input_charset)
            msgid2 = to_unicode(msgid2, encoding=self.input_charset)
            try:
                message = self._fallback.lngettext(msgid1, msgid2, n)
            except (AttributeError, UnicodeError):
                # Ignore UnicodeErrors: we'll do our own encoding next
                # AttributeError happens on py2.3 where lngettext is not
                # implemented
                pass

        # Make sure that we're returning a str
        if self._output_charset:
            return to_bytes(message, encoding=self._output_charset,
                    nonstring='empty')
        return to_bytes(message, encoding=locale.getpreferredencoding(),
                nonstring='empty')

    def ugettext(self, message):
        if not isinstance(message, basestring):
            return u''
        if self._fallback:
            msg = to_unicode(message, encoding=self.input_charset)
            try:
                message = self._fallback.ugettext(msg)
            except UnicodeError:
                # Ignore UnicodeErrors: We'll do our own decoding later
                pass

        # Make sure we're returning unicode
        return to_unicode(message, encoding=self.input_charset)

    def ungettext(self, msgid1, msgid2, n):
        # Default
        if n == 1:
            message = msgid1
        else:
            message = msgid2
        # Fallback might override this
        if self._fallback:
            msgid1 = to_unicode(msgid1, encoding=self.input_charset)
            msgid2 = to_unicode(msgid2, encoding=self.input_charset)
            try:
                message = self._fallback.ungettext(msgid1, msgid2, n)
            except UnicodeError:
                # Ignore UnicodeErrors: We'll do our own decoding later
                pass

        # Make sure we're returning unicode
        return to_unicode(message, encoding=self.input_charset,
                nonstring='empty')


class NewGNUTranslations(DummyTranslations, gettext.GNUTranslations):
    '''Safer version of :class:`gettext.GNUTranslations`

    :class:`gettext.GNUTranslations` suffers from two problems that this
    class fixes.

    1) :class:`gettext.GNUTranslations` can throw a
       :exc:`~exceptions.UnicodeError` in
       :meth:`gettext.GNUTranslations.ugettext` if the message being
       translated has non-:term:`ASCII` characters and there is no translation
       for it.
    2) :class:`gettext.GNUTranslations` can return byte :class:`str` from
       :meth:`gettext.GNUTranslations.ugettext` and :class:`unicode`
       strings from the other :meth:`~gettext.GNUTranslations.gettext`
       methods if the message being translated is the wrong type 

    When byte :class:`str` are returned, the strings will be encoded
    according to this algorithm:

    1) If a fallback has been added, the fallback will be called first.
       You'll need to consult the fallback to see whether it performs any
       encoding changes.
    2) If a byte :class:`str` was given, the same byte :class:`str` will
       be returned.
    3) If a :class:`unicode` string was given and
       :meth:`set_output_charset` has been called then we encode the
       string using the :attr:`output_charset`
    4) If a :class:`unicode` string was given and this is :meth:`gettext`
       or :meth:`ngettext` and a charset was detected when parsing the
       :term:`message catalog`, output in that charset.
    5) If a :class:`unicode` string was given and this is :meth:`gettext`
       or :meth:`ngettext` we encode it using :term:`UTF-8`.
    6) If a :class:`unicode` string was given and this is :meth:`lgettext`
       or :meth:`lngettext` we encode using the value of
       :func:`locale.getpreferredencoding`

    For :meth:`ugettext` and :meth:`ungettext`, we go through the same set of
    steps with the following differences:

    * We transform byte :class:`str` into :class:`unicode` strings for these
      methods.
    * The encoding used to decode the byte :class:`str` is taken from
      :attr:`input_charset` if it's set, otherwise we decode using
      :term:`UTF-8`

    .. attribute:: input_charset
    
        an extension to the |stdlib|_ :mod:`gettext` that specifies what
        charset a message is encoded in when decoding a message to
        :class:`unicode`.  This is used for two purposes:

    1) If the message string is a byte :class:`str`, this is used to decode
       the string to a :class:`unicode` string before looking it up in the
       :term:`message catalog`.
    2) In :meth:`~kitchen.i18n.DummyTranslations.ugettext` and
       :meth:`~kitchen.i18n.DummyTranslations.ungettext` methods, if a byte
       :class:`str` is given as the message and is untranslated his is used as
       the encoding when decoding to :class:`unicode`.  This is different from
       the :attr:`_charset` parameter that may be set when a :term:`message
       catalog` is loaded because :attr:`input_charset` is used to describe an
       encoding used in a python source file while :attr:`_charset` describes
       the encoding used in the :term:`message catalog` file.

    Any characters that aren't able to be transformed from a byte
    :class:`str` to :class:`unicode` string or vice versa will be replaced
    with a replacement character (ie: ``u'�'`` in unicode based encodings,
    ``'?'`` in other :term:`ASCII` compatible encodings).

    .. seealso::

        :class:`gettext.GNUTranslations.gettext`
            For information about what methods this class has and what they do

    '''
    #pylint: disable-msg=C0103,C0111
    def _parse(self, fp):
        gettext.GNUTranslations._parse(self, fp)

    def gettext(self, message):
        if not isinstance(message, basestring):
            return ''
        tmsg = message
        message = to_unicode(message, encoding=self.input_charset)
        try:
            tmsg = self._catalog[message] #pylint:disable-msg=E1101
        except KeyError:
            if self._fallback:
                try:
                    tmsg = self._fallback.gettext(message)
                except UnicodeError:
                    # Ignore UnicodeErrors: We'll do our own encoding next
                    pass

        # Make sure that we're returning a str
        if self._output_charset:
            return to_bytes(tmsg, encoding=self._output_charset)
        elif self._charset:
            return to_bytes(tmsg, encoding=self._charset)
        return to_bytes(tmsg)

    def ngettext(self, msgid1, msgid2, n):
        if n == 1:
            tmsg = msgid1
        else:
            tmsg = msgid2

        if not isinstance(msgid1, basestring):
            return ''
        msgid1 = to_unicode(msgid1, encoding=self.input_charset)
        try:
            #pylint:disable-msg=E1101
            tmsg = self._catalog[(msgid1, self.plural(n))]
        except KeyError:
            if self._fallback:
                try:
                    tmsg = self._fallback.ngettext(msgid1, msgid2, n)
                except UnicodeError:
                    # Ignore UnicodeErrors: We'll do our own encoding next
                    pass

        # Make sure that we're returning a str
        if self._output_charset:
            return to_bytes(tmsg, encoding=self._output_charset,
                    nonstring='empty')
        elif self._charset:
            return to_bytes(tmsg, encoding=self._charset, nonstring='empty')
        return to_bytes(tmsg, nonstring='empty')

    def lgettext(self, message):
        if not isinstance(message, basestring):
            return ''
        tmsg = message
        message = to_unicode(message, encoding=self.input_charset)
        try:
            tmsg = self._catalog[message] #pylint:disable-msg=E1101
        except KeyError:
            if self._fallback:
                try:
                    tmsg = self._fallback.lgettext(message)
                except UnicodeError:
                    # Ignore UnicodeErrors: We'll do our own encoding next
                    pass

        # Make sure that we're returning a str
        if self._output_charset:
            return to_bytes(tmsg, encoding=self._output_charset)
        return to_bytes(tmsg, encoding=locale.getpreferredencoding())

    def lngettext(self, msgid1, msgid2, n):
        if n == 1:
            tmsg = msgid1
        else:
            tmsg = msgid2

        if not isinstance(msgid1, basestring):
            return ''
        msgid1 = to_unicode(msgid1, encoding=self.input_charset)
        try:
            #pylint:disable-msg=E1101
            tmsg = self._catalog[(msgid1, self.plural(n))]
        except KeyError:
            if self._fallback:
                try:
                    tmsg = self._fallback.ngettext(msgid1, msgid2, n)
                except UnicodeError:
                    # Ignore UnicodeErrors: We'll do our own encoding next
                    pass

        # Make sure that we're returning a str
        if self._output_charset:
            return to_bytes(tmsg, encoding=self._output_charset,
                    nonstring='empty')
        return to_bytes(tmsg, encoding=locale.getpreferredencoding(),
                nonstring='empty')

    def ugettext(self, message):
        if not isinstance(message, basestring):
            return u''
        message = to_unicode(message, encoding=self.input_charset)
        try:
            message = self._catalog[message] #pylint:disable-msg=E1101
        except KeyError:
            if self._fallback:
                try:
                    message = self._fallback.ugettext(message)
                except UnicodeError:
                    # Ignore UnicodeErrors: We'll do our own encoding next
                    pass

        # Make sure that we're returning unicode
        return to_unicode(message, encoding=self.input_charset)

    def ungettext(self, msgid1, msgid2, n):
        if n == 1:
            tmsg = msgid1
        else:
            tmsg = msgid2

        if not isinstance(msgid1, basestring):
            return u''
        msgid1 = to_unicode(msgid1, encoding=self.input_charset)
        try:
            #pylint:disable-msg=E1101
            tmsg = self._catalog[(msgid1, self.plural(n))]
        except KeyError:
            if self._fallback:
                try:
                    tmsg = self._fallback.ungettext(msgid1, msgid2, n)
                except UnicodeError:
                    # Ignore UnicodeErrors: We'll do our own encoding next
                    pass

        # Make sure that we're returning unicode
        return to_unicode(tmsg, encoding=self.input_charset,
                nonstring='empty')


def get_translation_object(domain, localedirs=tuple()):
    '''Get a translation object bound to the :term:`message catalogs`

    :arg domain: Name of the message domain.  This should be a unique name
        that can be used to lookup the :term:`message catalog` for this app.
    :kwarg localedirs: Iterator of directories to look for :term:`message
        catalogs` under.  The first directory to exist is used regardless of
        whether messages for this domain are present.  If none of the
        directories exist, fallback on ``sys.prefix`` + :file:`/share/locale`
        Default: No directories to search; just use the fallback.
    :return: Translation object to get :mod:`gettext` methods from

    If you need more flexibility than :func:`easy_gettext_setup`, use this
    function.  It sets up a :mod:`gettext` Translation object and returns it
    to you.  Then you can access any of the methods of the object that you
    need directly.  For instance, if you specifically need to access
    :func:`~gettext.GNUTranslations.lgettext`::

        translations = get_translation_object('foo')
        translations.lgettext('My Message')

    Setting up :mod:`gettext` in a portable manner can be a little tricky due
    to not having a common directory for translations across operating
    systems.  :func:`get_translation_object` is able to handle that if you give
    it a list of directories to search for catalogs::

        translations = get_translation_object('foo', localedirs=(
             os.path.join(os.path.realpath(os.path.dirname(__file__)), 'locale'),
             os.path.join(sys.prefix, 'lib', 'locale')))

    This will search for several different directories:

    1. A directory named :file:`locale` in the same directory as the module
       that called :func:`get_translation_object`,
    2. In :file:`/usr/lib/locale`
    3. In :file:`/usr/share/locale` (the fallback directory)

    This allows :mod:`gettext` to work on Windows and in development (where the
    :term:`message catalogs` are typically in the toplevel module directory)
    and also when installed under Linux (where the :term:`message catalogs`
    are installed in :file:`/usr/share/locale`).  You (or the system packager)
    just need to install the :term:`message catalogs` in
    :file:`/usr/share/locale` and remove the :file:`locale` directory from the
    module to make this work.  ie::

        In development:
            ~/foo   # Toplevel module directory
            ~/foo/__init__.py
            ~/foo/locale    # With message catalogs below here:
            ~/foo/locale/es/LC_MESSAGES/foo.mo

        Installed on Linux:
            /usr/lib/python2.7/site-packages/foo
            /usr/lib/python2.7/site-packages/foo/__init__.py
            /usr/share/locale/  # With message catalogs below here:
            /usr/share/locale/es/LC_MESSAGES/foo.mo

    .. warning:: The first directory that we can access will be used
        regardless of whether locale files for our domain and language are
        present in the directory.  That means you have to consider the order
        in which you list directories in :attr:`localedirs`.  Always list
        directories which you, the user, or the system packager can control
        the existence of before system directories that will exist whether or
        not the :term:`message catalogs` are present in them.

    .. note:: This function returns either :class:`DummyTranslations` or
        :class:`NewGNUTranslations`.  These classes are superior to their
        :mod:`gettext` equivalents as described in their documentation.
    '''
    # Look for the message catalogs in several places.  This allows for use
    # with uninstalled modules, installed modules on Linux, and modules
    # installed on platforms where the module locales are in the module dir

    for localedir in localedirs:
        if os.access(localedir, os.R_OK | os.X_OK) \
                and os.path.isdir(localedir):
            break
    else:  # Note: yes, this else is intended to go with the for
        localedir = os.path.join(sys.prefix, 'share', 'locale')

    try:
        # localedir is always initialized in the above code.  pylint doesn't
        # recognize that the for: else will initialize it.
        #pylint:disable-msg=W0631
        translations = gettext.translation(domain, localedir=localedir,
                class_=NewGNUTranslations, fallback=False)
    except IOError:
        # basically, we're providing our own fallback here since
        # gettext.NullTranslations doesn't guarantee that unicode and str is
        # respected
        translations = DummyTranslations()

    return translations

def easy_gettext_setup(domain, localedirs=tuple(), use_unicode=True):
    ''' Setup translation functions for an application

    :arg domain: Name of the message domain.  This should be a unique name
        that can be used to lookup the :term:`message catalog` for this app.
    :kwarg localedirs: Iterator of directories to look for :term:`message
        catalogs` under.  The first directory to exist is used regardless of
        whether messages for this domain are present.  If none of the
        directories exist, fallback on ``sys.prefix`` + :file:`/share/locale`
        Default: No directories to search so we just use the fallback.
    :kwarg use_unicode: If :data:`True` return the :mod:`gettext` functions
        for :class:`unicode` strings else return the functions for byte
        :class:`str` for the translations.  Default is :data:`True`.
    :return: tuple of the :mod:`gettext` function and :mod:`gettext` function
        for plurals

    Setting up :mod:`gettext` can be a little tricky because of lack of
    documentation.  This function will setup :mod:`gettext`  using the 
    `Class-based API
    <http://docs.python.org/library/gettext.html#class-based-api>`_ for you.
    For the simple case, you can use the default arguments and call it like
    this::

        _, N_ = easy_gettext_setup()

    This will get you two functions, :func:`_` and :func:`N_` that you can use
    to mark strings in your code for translation.  :func:`_` is used to mark
    strings that don't need to worry about plural forms no matter what the
    value of the variable is.  :func:`N_` is used to mark strings that do need
    to have a different form if a variable in the string is plural.

    .. seealso::

        :doc:`api-i18n`
            This module's documentation has examples of using :func:`_` and :func:`N_`
        :func:`get_translation_object`
            for information on how to use :attr:`localedirs` to get the
            proper :term:`message catalogs` both when in development and when
            installed to FHS compliant directories on Linux.

    .. note:: The gettext functions returned from this function should be
        superior to the ones returned from :mod:`gettext`.  The traits that
        make them better are described in the :class:`DummyTranslations` and
        :class:`NewGNUTranslations` documentation.

    .. versionchanged:: kitchen-0.2.4 ; API kitchen.i18n 2.0.0
        Changed :func:`~kitchen.i18n.easy_gettext_setup` to return the lgettext
        functions instead of gettext functions when use_unicode=False.
    '''
    translations = get_translation_object(domain, localedirs=localedirs)
    if use_unicode:
        return(translations.ugettext, translations.ungettext)
    return(translations.lgettext, translations.lngettext)

__all__ = ('DummyTranslations', 'NewGNUTranslations', 'easy_gettext_setup',
        'get_translation_object')
