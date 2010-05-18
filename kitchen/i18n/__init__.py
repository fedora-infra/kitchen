# -*- coding: utf-8 -*-
#
# Copyright (c) 2010 Red Hat, Inc
# Copyright (c) 2009 Milos Komarcevic
# Copyright (c) 2008 Tim Lauridsen
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#   James Antill
#   Milos Komarcevic
#   Toshio Kuratomi <toshio@fedoraproject.org>
#   Tim Lauridsen
#   Luke Macken <lmacken@redhat.com>
#   Seth Vidal <skvidal@fedoraproject.org>
#
# Portions of code taken from yum/i18n.py

__version__ = '0.1'

import gettext
import locale
import os
import sys

class DummyTranslations(gettext.NullTranslations):
    def __init__(self, fp=None):
        '''Safer version of NullTranslations

        This Translations class doesn't translate the strings and is mostly
        meant for times when there were errors setting up a real Translations
        object.  It's safer than gettext.NullTranslations in its
        handling of byte strings vs unicode strings.  Unlike NullTranslations,
        this Translation class will never throw a UnicodeError.  Also, like
        GNUTranslations, all of this Translation object's methods guarantee to
        return byte strings except for ugettext and ungettext which guarantee
        to return unicode strings.

        When byte strings are returned, the strings will be encoded according
        to this algorithm:

        1) If a fallback has been added, the fallback will be called first.
            You'll need to consult the fallback to see whether it performs any
            encoding changes.
        2) If a byte string was given, the same byte string will be returned.
        3) If a unicode string was given and :meth:`set_output_charset` has 
            been called then we encode the string using the
            :attr:`output_charset`
        4) If a unicode string was given and this is :meth:`gettext` or
            :meth:`ngettext` we encode it using 'utf8'.
        5) If a unicode string was given and this is :meth:`lgettext` or
            :meth:`lngettext` and we encode using the value of
            :func:`locale.getpreferredencoding`

        For :meth:`ugettext` and :meth:`ungettext`, we go through the same
        set of steps with the following differences:

        * We transform byte strings into unicode strings for these methods.
        * The encoding used to decode the byte strings is taken from
            :attr:`_charset` if it's set, otherwise we decode using 'utf8'.

        .. seealso::
            :class:`gettext.NullTranslation`
                for information about what each of these methods do

        '''
        # Import this here to avoid circular deps with kitchen.text
        from kitchen.text.converters import to_unicode, to_bytes
        self.to_unicode = to_unicode
        self.to_bytes = to_bytes
        gettext.NullTranslations.__init__(self, fp)

    def gettext(self, message):
        try:
            message = gettext.NullTranslations.gettext(self, message)
        except UnicodeError:
            # Ignore UnicodeErrors: We'll do our own encoding next
            pass
        if self._output_charset:
            return self.to_bytes(message, encoding=self._output_charset)
        return self.to_bytes(message)

    def ngettext(self, msgid1, msgid2, n):
        try:
            message = gettext.NullTranslations.ngettext(self, msgid1, msgid2, n)
        except UnicodeError:
            pass
        if self._output_charset:
            return self.to_bytes(message, encoding=self._output_charset)
        return self.to_bytes(message)

    def lgettext(self, message):
        try:
            message = gettext.NullTranslations.lgettext(self, message)
        except UnicodeError:
            # Ignore UnicodeErrors: we'll do our own encoding next
            pass
        if self._output_charset:
            return self.to_bytes(message, encoding=self._output_charset)
        return self.to_bytes(message, encoding=locale.getpreferredencoding())

    def lngettext(self, msgid1, msgid2, n):
        try:
            message = gettext.NullTranslations.lngettext(self, msgid1, msgid2, n)
        except UnicodeError:
            pass
        if self._output_charset:
            return self.to_bytes(message, encoding=self._output_charset)
        return self.to_bytes(message, encoding=locale.getpreferredencoding())

    def ugettext(self, message):
        try:
            message = gettext.NullTranslations.ugettext(self, message)
        except UnicodeError:
            # Ignore UnicodeErrors: We'll do our own decoding later
            pass
        if self._charset:
            return self.to_unicode(message, encoding=self._charset)
        return self.to_unicode(message)

    def ungettext(self, msgid1, msgid2, n):
        try:
            message = gettext.NullTranslations.ungettext(self, msgid1, msgid2, n)
        except UnicodeError:
            if n == 1:
                message = msgid1
            else:
                message = msgid2
        if self._charset:
            return self.to_unicode(message, encoding=self._charset)
        return self.to_unicode(message)


def get_translation_object(domain, localedirs=tuple()):
    '''Get a translation object bound to the message catalogs

    :arg domain: Name of the message domain
    :kwarg localedirs: Iterator of directories to look for message catalogs
        under.  The first directory to exist is used regardless of messages
        for this domain are present.  If none of the directories exist,
        fallback on sys.prefix + '/share/locale'  Default: No directories to
        search.
    :return: Translation object to get gettext methods from

    If you need more flexibility than :func:`easy_gettext_setup`, use this
    function.  It sets up a gettext Translation object and returns it to you.
    Then you can access any of the methods of the object that you need
    directly.  For instance, if you specifically need to access lgettext::

        translations = get_translation_object('foo')
        translations.lgettext('My Message')

    Setting up gettext in a portable manner can be a little tricky due to not
    having a common directory for translations across operating systems.
    :func:`get_translation_object` is able to handle that by giving it a list
    of directories::

        translations = get_translation_object('foo', localedirs=(
                os.path.join(os.path.realpath(os.path.dirname(__file__)), 'locale'),
                os.path.join(sys.prefix, 'lib', 'locale')))

    This will search for several different directories:

    1) A directory named 'locale' in the same directory as the module that
        called :func:`get_translation_object`,
    2) In :file:`/usr/lib/locale`
    3) In :file:`/usr/share/locale` (the fallback directory)

    The first of these that are a directory we can access will be used
    (regardless of whether any locale files are present in the directory.)
    This allows gettext to work on Windows and in development (where the
    locale files are typically in the toplevel module directory) and also when
    installed under Linux (where the message catalogs are installed in
    /usr/share/locale).  You (or the Linux packager) just need to place the
    locale files in /usr/share/locale and remove the locale directory from the
    module to make this work.  ie::

        In development:
            ~/foo   # Toplevel module directory
            ~/foo__init__.py
            ~/foo/locale    # With message catalogs below here:
            ~/foo/locale/es/LC_MESSAGES/foo.mo

        Installed on Linux:
            /usr/lib/python2.6/site-packages/foo
            /usr/lib/python2.6/site-packages/foo/__init__.py
            /usr/share/locale/  # With message catalogs below here:
            /usr/share/locale/es/LC_MESSAGES/foo.mo
    '''
    # Look for the message catalogs in several places.  This allows for use
    # with uninstalled modules, installed modules on Linux, and modules
    # installed on platforms where the module locales are in the module dir

    for localedir in localedirs:
        if os.access(localedir, os.R_OK | os.X_OK) and os.path.isdir(localedir):
            break
    else:  # Note: yes, this else is intended to go with the for
        localedir = os.path.join(sys.prefix, 'share', 'locale')

    try:
        translations = gettext.translation(domain, localedir=localedir, fallback=True)
    except:
        translations = DummyTranslations()
    return translations

def easy_gettext_setup(domain, localedirs=tuple(), use_unicode=True):
    ''' Setup translation domain for this app.

    :arg domain: Name of the message domain
    :kwarg localedirs: Iterator of directories to look for message catalogs
        under.  The first directory to exist is used regardless of messages
        for this domain are present.  If none of the directories exist,
        fallback on sys.prefix + '/share/locale'  Default: No directories to
        search.
    :kwarg use_unicode: If True return unicode strings else return byte
        strings for the translations.  Default is True
    :return: tuple of the gettext function and gettext function for plurals

    Setting up gettext can be a little tricky because of lack of documentation.
    This function will setup gettext for you and hopefully supplement the docs
    so you can understand how to do things sensibly.  For the simple case, you
    can use the default arguments and call us like this::

        _, N_ = setup_gettext()

    This will get you two functions, _() and N_() that you can use to mark
    strings in your code for translation.

    .. seealso::
        :func:`get_translation_object`
            for information on how to use :attr:`localedirs` to get the
            proper message catalogs both when in development or when installed
            to FHS compliant directories on Linux.
    '''
    translations = get_translation_object(domain, localedirs=localedirs)
    if use_unicode:
        _ = translations.ugettext
        N_ = translations.ungettext
    else:
        _ = translations.gettext
        N_ = translations.ngettext

    return (_, N_)

__all__ = (DummyTranslations, easy_gettext_setup, get_translation_object)
