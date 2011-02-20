# -*- coding: utf-8 -*-
#
import unittest
from nose import tools

import os
import types

from kitchen import i18n

import base_classes

class TestI18N_UTF8(unittest.TestCase):
    def setUp(self):
        self.old_LC_ALL = os.environ.get('LC_ALL', None)
        os.environ['LC_ALL'] = 'pt_BR.UTF8'

    def tearDown(self):
        if self.old_LC_ALL:
            os.environ['LC_ALL'] = self.old_LC_ALL
        else:
            del(os.environ['LC_ALL'])

    def test_easy_gettext_setup(self):
        '''Test that the easy_gettext_setup function works
        '''
        _, N_ = i18n.easy_gettext_setup('foo', localedirs=
                ['%s/data/locale/' % os.path.dirname(__file__)])
        tools.ok_(isinstance(_, types.MethodType))
        tools.ok_(isinstance(N_, types.MethodType))
        tools.ok_(_.im_func.func_name == 'ugettext')
        tools.ok_(N_.im_func.func_name == 'ungettext')

        tools.ok_(_('café') == u'café')
        tools.ok_(_(u'café') == u'café')
        tools.ok_(N_('café', 'cafés', 1) == u'café')
        tools.ok_(N_('café', 'cafés', 2) == u'cafés')
        tools.ok_(N_(u'café', u'cafés', 1) == u'café')
        tools.ok_(N_(u'café', u'cafés', 2) == u'cafés')

    def test_easy_gettext_setup_non_unicode(self):
        '''Test that the easy_gettext_setup function works
        '''
        b_, bN_ = i18n.easy_gettext_setup('foo', localedirs=
                ['%s/data/locale/' % os.path.dirname(__file__)],
                use_unicode=False)
        tools.ok_(isinstance(b_, types.MethodType))
        tools.ok_(isinstance(bN_, types.MethodType))
        tools.ok_(b_.im_func.func_name == 'lgettext')
        tools.ok_(bN_.im_func.func_name == 'lngettext')

        tools.ok_(b_('café') == 'café')
        tools.ok_(b_(u'café') == 'café')
        tools.ok_(bN_('café', 'cafés', 1) == 'café')
        tools.ok_(bN_('café', 'cafés', 2) == 'cafés')
        tools.ok_(bN_(u'café', u'cafés', 1) == 'café')
        tools.ok_(bN_(u'café', u'cafés', 2) == 'cafés')

    def test_get_translation_object(self):
        '''Test that the get_translation_object function works
        '''
        translations = i18n.get_translation_object('foo', ['%s/data/locale/' % os.path.dirname(__file__)])
        tools.ok_(translations.__class__==i18n.DummyTranslations)

        translations = i18n.get_translation_object('test', ['%s/data/locale/' % os.path.dirname(__file__)])
        tools.ok_(translations.__class__==i18n.NewGNUTranslations)

    def test_dummy_translation(self):
        '''Test that we can create a DummyTranslation obejct
        '''
        tools.ok_(isinstance(i18n.DummyTranslations(), i18n.DummyTranslations))

# Note: Using nose's generator tests for this so we can't subclass
# unittest.TestCase
class TestDummyTranslations(base_classes.UnicodeTestData):
    def __init__(self):
        self.test_data = {'bytes': (( # First set is with default charset (utf8)
                (self.u_ascii, self.b_ascii),
                (self.u_spanish, self.utf8_spanish),
                (self.u_japanese, self.utf8_japanese),
                (self.b_ascii, self.b_ascii),
                (self.utf8_spanish, self.utf8_spanish),
                (self.latin1_spanish, self.latin1_spanish),
                (self.utf8_japanese, self.utf8_japanese),
                ),
                ( # Second set is with output_charset of latin1 (ISO-8859-1)
                (self.u_ascii, self.b_ascii),
                (self.u_spanish, self.latin1_spanish),
                (self.u_japanese, self.latin1_japanese_replace),
                (self.b_ascii, self.b_ascii),
                (self.utf8_spanish, self.utf8_spanish),
                (self.latin1_spanish, self.latin1_spanish),
                (self.utf8_japanese, self.utf8_japanese),
                ),
                ( # Third set is with output_charset of C
                (self.u_ascii, self.b_ascii),
                (self.u_spanish, self.ascii_spanish_replace),
                (self.u_japanese, self.ascii_japanese_replace),
                (self.b_ascii, self.b_ascii),
                (self.utf8_spanish, self.utf8_spanish),
                (self.latin1_spanish, self.latin1_spanish),
                (self.utf8_japanese, self.utf8_japanese),
                ),
            ),
            'unicode': (( # First set is with the default charset (utf8)
                (self.u_ascii, self.u_ascii),
                (self.u_spanish, self.u_spanish),
                (self.u_japanese, self.u_japanese),
                (self.b_ascii, self.u_ascii),
                (self.utf8_spanish, self.u_spanish),
                (self.latin1_spanish, self.u_spanish_replace), # String is mangled but no exception
                (self.utf8_japanese, self.u_japanese),
                ),
                ( # Second set is with _charset of latin1 (ISO-8859-1)
                (self.u_ascii, self.u_ascii),
                (self.u_spanish, self.u_spanish),
                (self.u_japanese, self.u_japanese),
                (self.b_ascii, self.u_ascii),
                (self.utf8_spanish, self.u_mangled_spanish_utf8_as_latin1), # String mangled but no exception
                (self.latin1_spanish, self.u_spanish),
                (self.utf8_japanese, self.u_mangled_japanese_utf8_as_latin1), # String mangled but no exception
                ),
                ( # Third set is with _charset of C
                (self.u_ascii, self.u_ascii),
                (self.u_spanish, self.u_spanish),
                (self.u_japanese, self.u_japanese),
                (self.b_ascii, self.u_ascii),
                (self.utf8_spanish, self.u_mangled_spanish_utf8_as_ascii
                    ), # String mangled but no exception
                (self.latin1_spanish, self.u_mangled_spanish_latin1_as_ascii), # String mangled but no exception
                (self.utf8_japanese, self.u_mangled_japanese_utf8_as_ascii), # String mangled but no exception
                ),
            )
    }

    def setUp(self):
        self.translations = i18n.DummyTranslations()

    def check_gettext(self, message, value, charset=None):
        self.translations.set_output_charset(charset)
        tools.ok_(self.translations.gettext(message) == value)

    def check_lgettext(self, message, value, charset=None, locale='en_US.UTF-8'):
        os.environ['LC_ALL'] = locale
        self.translations.set_output_charset(charset)
        tools.ok_(self.translations.lgettext(message) == value)

    # Note: charset has a default value because nose isn't invoking setUp and
    # tearDown each time check_* is run.
    def check_ugettext(self, message, value, charset='utf-8'):
        '''ugettext method with default values'''
        self.translations.input_charset = charset
        tools.ok_(self.translations.ugettext(message) == value)

    def check_ngettext(self, message, value, charset=None):
        self.translations.set_output_charset(charset)
        tools.ok_(self.translations.ngettext(message, 'blank', 1) == value)
        tools.ok_(self.translations.ngettext('blank', message, 2) == value)
        tools.ok_(self.translations.ngettext(message, 'blank', 2) != value)
        tools.ok_(self.translations.ngettext('blank', message, 1) != value)

    def check_lngettext(self, message, value, charset=None, locale='en_US.UTF-8'):
        os.environ['LC_ALL'] = locale
        self.translations.set_output_charset(charset)
        tools.ok_(self.translations.lngettext(message, 'blank', 1) == value)
        tools.ok_(self.translations.lngettext('blank', message, 2) == value)
        tools.ok_(self.translations.lngettext(message, 'blank', 2) != value)
        tools.ok_(self.translations.lngettext('blank', message, 1) != value)

    # Note: charset has a default value because nose isn't invoking setUp and
    # tearDown each time check_* is run.
    def check_ungettext(self, message, value, charset='utf-8'):
        self.translations.input_charset = charset
        tools.ok_(self.translations.ungettext(message, 'blank', 1) == value)
        tools.ok_(self.translations.ungettext('blank', message, 2) == value)
        tools.ok_(self.translations.ungettext(message, 'blank', 2) != value)
        tools.ok_(self.translations.ungettext('blank', message, 1) != value)

    def test_gettext(self):
        '''gettext method with default values'''
        for message, value in self.test_data['bytes'][0]:
            yield self.check_gettext, message, value

    def test_gettext_output_charset(self):
        '''gettext method after output_charset is set'''
        for message, value in self.test_data['bytes'][1]:
            yield self.check_gettext, message, value, 'latin1'

    def test_ngettext(self):
        for message, value in self.test_data['bytes'][0]:
            yield self.check_ngettext, message, value

    def test_ngettext_output_charset(self):
        for message, value in self.test_data['bytes'][1]:
            yield self.check_ngettext, message, value, 'latin1'

    def test_lgettext(self):
        '''lgettext method with default values on a utf8 locale'''
        for message, value in self.test_data['bytes'][0]:
            yield self.check_lgettext, message, value

    def test_lgettext_output_charset(self):
        '''lgettext method after output_charset is set'''
        for message, value in self.test_data['bytes'][1]:
            yield self.check_lgettext, message, value, 'latin1'

    def test_lgettext_output_charset_and_locale(self):
        '''lgettext method after output_charset is set in C locale

        output_charset should take precedence
        '''
        for message, value in self.test_data['bytes'][1]:
            yield self.check_lgettext, message, value, 'latin1', 'C'

    def test_lgettext_locale_C(self):
        '''lgettext method in a C locale'''
        for message, value in self.test_data['bytes'][2]:
            yield self.check_lgettext, message, value, None, 'C'

    def test_lngettext(self):
        '''lngettext method with default values on a utf8 locale'''
        for message, value in self.test_data['bytes'][0]:
            yield self.check_lngettext, message, value

    def test_lngettext_output_charset(self):
        '''lngettext method after output_charset is set'''
        for message, value in self.test_data['bytes'][1]:
            yield self.check_lngettext, message, value, 'latin1'

    def test_lngettext_output_charset_and_locale(self):
        '''lngettext method after output_charset is set in C locale

        output_charset should take precedence
        '''
        for message, value in self.test_data['bytes'][1]:
            yield self.check_lngettext, message, value, 'latin1', 'C'

    def test_lngettext_locale_C(self):
        '''lngettext method in a C locale'''
        for message, value in self.test_data['bytes'][2]:
            yield self.check_lngettext, message, value, None, 'C'

    def test_ugettext(self):
        for message, value in self.test_data['unicode'][0]:
            yield self.check_ugettext, message, value

    def test_ugettext_charset_latin1(self):
        for message, value in self.test_data['unicode'][1]:
            yield self.check_ugettext, message, value, 'latin1'

    def test_ugettext_charset_ascii(self):
        for message, value in self.test_data['unicode'][2]:
            yield self.check_ugettext, message, value, 'ascii'

    def test_ungettext(self):
        for message, value in self.test_data['unicode'][0]:
            yield self.check_ungettext, message, value

    def test_ungettext_charset_latin1(self):
        for message, value in self.test_data['unicode'][1]:
            yield self.check_ungettext, message, value, 'latin1'

    def test_ungettext_charset_ascii(self):
        for message, value in self.test_data['unicode'][2]:
            yield self.check_ungettext, message, value, 'ascii'

    def test_nonbasestring(self):
        tools.ok_(self.translations.gettext(dict(hi='there')) == '')
        tools.ok_(self.translations.ngettext(dict(hi='there'), dict(hi='two'), 1) == '')
        tools.ok_(self.translations.lgettext(dict(hi='there')) == '')
        tools.ok_(self.translations.lngettext(dict(hi='there'), dict(hi='two'), 1) == '')
        tools.ok_(self.translations.ugettext(dict(hi='there')) == u'')
        tools.ok_(self.translations.ungettext(dict(hi='there'), dict(hi='two'), 1) == u'')


class TestI18N_Latin1(unittest.TestCase):
    def setUp(self):
        self.old_LC_ALL = os.environ.get('LC_ALL', None)
        os.environ['LC_ALL'] = 'pt_BR.ISO8859-1'

    def tearDown(self):
        if self.old_LC_ALL:
            os.environ['LC_ALL'] = self.old_LC_ALL
        else:
            del(os.environ['LC_ALL'])

    def test_easy_gettext_setup_non_unicode(self):
        '''Test that the easy_gettext_setup function works
        '''
        b_, bN_ = i18n.easy_gettext_setup('foo', localedirs=
                ['%s/data/locale/' % os.path.dirname(__file__)],
                use_unicode=False)

        tools.ok_(b_('café') == 'café')
        tools.ok_(b_(u'café') == 'caf\xe9')
        tools.ok_(bN_('café', 'cafés', 1) == 'café')
        tools.ok_(bN_('café', 'cafés', 2) == 'cafés')
        tools.ok_(bN_(u'café', u'cafés', 1) == 'caf\xe9')
        tools.ok_(bN_(u'café', u'cafés', 2) == 'caf\xe9s')


class TestNewGNUTranslationsFallback(TestDummyTranslations):
    def setUp(self):
        self.old_LC_ALL = os.environ.get('LC_ALL', None)
        os.environ['LC_ALL'] = 'pt_BR.utf8'
        self.translations = i18n.get_translation_object('test', ['%s/data/locale/' % os.path.dirname(__file__)])

    def tearDown(self):
        if self.old_LC_ALL:
            os.environ['LC_ALL'] = self.old_LC_ALL
        else:
            del(os.environ['LC_ALL'])


class TestNewGNURealTranslations_UTF8(unittest.TestCase):
    def setUp(self):
        self.old_LC_ALL = os.environ.get('LC_ALL', None)
        os.environ['LC_ALL'] = 'pt_BR.UTF8'
        self.translations = i18n.get_translation_object('test', ['%s/data/locale/' % os.path.dirname(__file__)])

    def tearDown(self):
        if self.old_LC_ALL:
            os.environ['LC_ALL'] = self.old_LC_ALL
        else:
            del(os.environ['LC_ALL'])

    def test_gettext(self):
        _ = self.translations.gettext
        tools.ok_(_('kitchen sink')=='pia da cozinha')
        tools.ok_(_('Kuratomi')=='くらとみ')
        tools.ok_(_('くらとみ')=='Kuratomi')

        tools.ok_(_(u'kitchen sink')=='pia da cozinha')
        tools.ok_(_(u'くらとみ')=='Kuratomi')
        tools.ok_(_(u'Kuratomi')=='くらとみ')

    def test_ngettext(self):
        _ = self.translations.ngettext
        tools.ok_(_('1 lemon', '4 lemons', 1)=='一 limão')
        tools.ok_(_('一 limão', '四 limões', 1)=='1 lemon')
        tools.ok_(_(u'1 lemon', u'4 lemons', 1)=='一 limão')
        tools.ok_(_(u'一 limão', u'四 limões', 1)=='1 lemon')

        tools.ok_(_('1 lemon', '4 lemons', 2)=='四 limões')
        tools.ok_(_('一 limão', '四 limões', 2)=='4 lemons')
        tools.ok_(_(u'1 lemon', u'4 lemons', 2)=='四 limões')
        tools.ok_(_(u'一 limão', u'四 limões', 2)=='4 lemons')

    def test_lgettext(self):
        _ = self.translations.lgettext
        tools.ok_(_('kitchen sink')=='pia da cozinha')
        tools.ok_(_('Kuratomi')=='くらとみ')
        tools.ok_(_('くらとみ')=='Kuratomi')

        tools.ok_(_(u'kitchen sink')=='pia da cozinha')
        tools.ok_(_(u'くらとみ')=='Kuratomi')
        tools.ok_(_(u'Kuratomi')=='くらとみ')

    def test_lngettext(self):
        _ = self.translations.lngettext
        tools.ok_(_('1 lemon', '4 lemons', 1)=='一 limão')
        tools.ok_(_('一 limão', '四 limões', 1)=='1 lemon')
        tools.ok_(_(u'1 lemon', u'4 lemons', 1)=='一 limão')
        tools.ok_(_(u'一 limão', u'四 limões', 1)=='1 lemon')

        tools.ok_(_('1 lemon', '4 lemons', 2)=='四 limões')
        tools.ok_(_('一 limão', '四 limões', 2)=='4 lemons')
        tools.ok_(_(u'1 lemon', u'4 lemons', 2)=='四 limões')
        tools.ok_(_(u'一 limão', u'四 limões', 2)=='4 lemons')

    def test_ugettext(self):
        _ = self.translations.ugettext
        tools.ok_(_('kitchen sink')==u'pia da cozinha')
        tools.ok_(_('Kuratomi')==u'くらとみ')
        tools.ok_(_('くらとみ')==u'Kuratomi')

        tools.ok_(_(u'kitchen sink')==u'pia da cozinha')
        tools.ok_(_(u'くらとみ')==u'Kuratomi')
        tools.ok_(_(u'Kuratomi')==u'くらとみ')

    def test_ungettext(self):
        _ = self.translations.ungettext
        tools.ok_(_('1 lemon', '4 lemons', 1)==u'一 limão')
        tools.ok_(_('一 limão', '四 limões', 1)==u'1 lemon')
        tools.ok_(_(u'1 lemon', u'4 lemons', 1)==u'一 limão')
        tools.ok_(_(u'一 limão', u'四 limões', 1)==u'1 lemon')

        tools.ok_(_('1 lemon', '4 lemons', 2)==u'四 limões')
        tools.ok_(_('一 limão', '四 limões', 2)==u'4 lemons')
        tools.ok_(_(u'1 lemon', u'4 lemons', 2)==u'四 limões')
        tools.ok_(_(u'一 limão', u'四 limões', 2)==u'4 lemons')


class TestNewGNURealTranslations_Latin1(TestNewGNURealTranslations_UTF8):
    def setUp(self):
        self.old_LC_ALL = os.environ.get('LC_ALL', None)
        os.environ['LC_ALL'] = 'pt_BR.ISO8859-1'
        self.translations = i18n.get_translation_object('test', ['%s/data/locale/' % os.path.dirname(__file__)])

    def tearDown(self):
        if self.old_LC_ALL:
            os.environ['LC_ALL'] = self.old_LC_ALL
        else:
            del(os.environ['LC_ALL'])

    def test_lgettext(self):
        _ = self.translations.lgettext
        tools.ok_(_('kitchen sink')=='pia da cozinha')
        tools.ok_(_('Kuratomi')=='????')
        tools.ok_(_('くらとみ')=='Kuratomi')

        tools.ok_(_(u'kitchen sink')=='pia da cozinha')
        tools.ok_(_(u'くらとみ')=='Kuratomi')
        tools.ok_(_(u'Kuratomi')=='????')

    def test_lngettext(self):
        _ = self.translations.lngettext
        tools.ok_(_('1 lemon', '4 lemons', 1)=='? lim\xe3o')
        tools.ok_(_('一 limão', '四 limões', 1)=='1 lemon')
        tools.ok_(_(u'1 lemon', u'4 lemons', 1)=='? lim\xe3o')
        tools.ok_(_(u'一 limão', u'四 limões', 1)=='1 lemon')

        tools.ok_(_('1 lemon', '4 lemons', 2)=='? lim\xf5es')
        tools.ok_(_('一 limão', '四 limões', 2)=='4 lemons')
        tools.ok_(_(u'1 lemon', u'4 lemons', 2)=='? lim\xf5es')
        tools.ok_(_(u'一 limão', u'四 limões', 2)=='4 lemons')
