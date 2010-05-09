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

import codecs
import locale
import os
import sys

from kitchen.text.encoding import to_unicode

def dummy_wrapper(str):
    '''
    Dummy Translation wrapper, just returning the same string.
    '''
    return to_unicode(str)

def dummyP_wrapper(str1, str2, n):
    '''
    Dummy Plural Translation wrapper, just returning the singular or plural
    string.
    '''
    if n == 1:
        return str1
    else:
        return str2

def setup_gettext(catalog, use_unicode=True):
    ''' Setup translation domain for this app.

    :arg catalog: Name of the message catalog
    :kwarg use_unicode: If True return unicode strings else return byte
        strings.  Default is True
    :return: tuple of the gettext function and gettext function for plurals
    '''
    try:
        # Setup the translation domain and make _() and P_() translation wrappers
        # available.
        # using ugettext to make sure translated strings are in Unicode.
        import gettext
        t = gettext.translation(catalog, fallback=True)
        if use_unicode:
            _ = t.ugettext
            P_ = t.ungettext
        else:
            _ = t.gettext
            P_ = t.ngettext
    except:
        # Something went wrong so we make a dummy _() wrapper there is just
        # returning the same text
        _ = dummy_wrapper
        P_ = dummyP_wrapper

    return (_, P_)

### This looks somewhat yum specific
def setup_locale(override_codecs=True, override_time=False):
    # This test needs to be before locale.getpreferredencoding() as that
    # does setlocale(LC_CTYPE, "")
    try:
        locale.setlocale(locale.LC_ALL, '')
        # set time to C so that we output sane things in the logs (#433091)
        if override_time:
            locale.setlocale(locale.LC_TIME, 'C')
    except locale.Error, e:
        # default to C locale if we get a failure.
        print >> sys.stderr, 'Failed to set locale, defaulting to C'
        os.environ['LC_ALL'] = 'C'
        locale.setlocale(locale.LC_ALL, 'C')

    if override_codecs:
        sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
        sys.stdout.errors = 'replace'

### What is this supposed to do?  I think it's not doing it but I'm not sure
def get_my_lang_code():
    mylang = locale.getlocale(locale.LC_MESSAGES)
    if mylang == (None, None): # odd :)
        mylang = 'C'
    else:
        mylang = '.'.join(mylang)

    return mylang

__all__ = (dummy_wrapper, dummyP_wrapper, setup_gettext)
