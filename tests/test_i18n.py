# -*- coding: utf-8 -*-
#
import unittest
from nose import tools

from gettext import NullTranslations
import os
import types

from kitchen import i18n

class TestI18N(unittest.TestCase):
    def test_easy_gettext_setup(self):
        '''Test that the eay_gettext_setup function works
        '''
        _, N_ = i18n.easy_gettext_setup('foo')
        tools.ok_(isinstance(_, types.MethodType))
        tools.ok_(isinstance(N_, types.MethodType))
        tools.ok_(_.im_func.func_name == 'ugettext')
        tools.ok_(N_.im_func.func_name == 'ungettext')

    def test_easy_gettext_setup_non_unicode(self):
        '''Test that the eay_gettext_setup function works
        '''
        _, N_ = i18n.easy_gettext_setup('foo', use_unicode=False)
        tools.ok_(isinstance(_, types.MethodType))
        tools.ok_(isinstance(N_, types.MethodType))
        tools.ok_(_.im_func.func_name == 'gettext')
        tools.ok_(N_.im_func.func_name == 'ngettext')

    def test_get_translation_object(self):
        '''Test that the get_translation_object function works
        '''
        translations = i18n.get_translation_object('foo')
        tools.ok_(isinstance(translations, NullTranslations))

    def test_dummy_translation(self):
        '''Test that we can create a DummyTranslation obejct
        '''
        tools.ok_(isinstance(i18n.DummyTranslations(), i18n.DummyTranslations))

# Note: Using nose's generator tests for this so we can't subclass
# unittest.TestCase
class TestDummyTranslations(object):
    u_ascii = u'the quick brown fox jumped over the lazy dog'
    u_accent = u'café'
    u_kana = u'くらとみ'
    b_ascii = 'the quick brown fox jumped over the lazy dog'
    utf8_accent = 'caf\xc3\xa9'
    latin1_accent = 'caf\xe9'
    ascii_accent= 'caf?'
    utf8_kana = '\xe3\x81\x8f\xe3\x82\x89\xe3\x81\xa8\xe3\x81\xbf'
    latin1_kana = '????'
    ascii_kana = '????'

    test_data = {'bytes': (( # First set is with default charset (utf8)
                (u_ascii, b_ascii),
                (u_accent, utf8_accent),
                (u_kana, utf8_kana),
                (b_ascii, b_ascii),
                (utf8_accent, utf8_accent),
                (latin1_accent, latin1_accent),
                (utf8_kana, utf8_kana),
                ),
                ( # Second set is with output_charset of latin1 (ISO-8859-1)
                (u_ascii, b_ascii),
                (u_accent, latin1_accent),
                (u_kana, latin1_kana),
                (b_ascii, b_ascii),
                (utf8_accent, utf8_accent),
                (latin1_accent, latin1_accent),
                (utf8_kana, utf8_kana),
                ),
                ( # Third set is with output_charset of C
                (u_ascii, b_ascii),
                (u_accent, ascii_accent),
                (u_kana, ascii_kana),
                (b_ascii, b_ascii),
                (utf8_accent, utf8_accent),
                (latin1_accent, latin1_accent),
                (utf8_kana, utf8_kana),
                ),
            ),
            'unicode': (( # First set is with the default charset (utf8)
                (u_ascii, u_ascii),
                (u_accent, u_accent),
                (u_kana, u_kana),
                (b_ascii, u_ascii),
                (utf8_accent, u_accent),
                (latin1_accent, u'caf�'), # String is mangled but no exception
                (utf8_kana, u_kana),
                ),
                ( # Second set is with _charset of latin1 (ISO-8859-1)
                (u_ascii, u_ascii),
                (u_accent, u_accent),
                (u_kana, u_kana),
                (b_ascii, u_ascii),
                (utf8_accent, u'cafÃ©'), # String mangled but no exception
                (latin1_accent, u_accent),
                (utf8_kana, u'\xe3\x81\x8f\xe3\x82\x89\xe3\x81\xa8\xe3\x81\xbf'), # String mangled but no exception
                ),
                ( # Third set is with _charset of C
                (u_ascii, u_ascii),
                (u_accent, u_accent),
                (u_kana, u_kana),
                (b_ascii, u_ascii),
                (utf8_accent, u'caf��'), # String mangled but no exception
                (latin1_accent, u'caf�'), # String mangled but no exception
                (utf8_kana, u'������������'), # String mangled but no exception
                ),
            )
    }

    def setUp(self):
        self.translations = i18n.DummyTranslations()

    def check_gettext(self, message, value, charset=None):
        if charset:
            self.translations.set_output_charset(charset)
        tools.ok_(self.translations.gettext(message) == value)

    def check_lgettext(self, message, value, charset=None, locale='en_US.UTF-8'):
        os.environ['LC_ALL'] = locale
        if charset:
            self.translations.set_output_charset(charset)
        tools.ok_(self.translations.lgettext(message) == value)

    def check_ugettext(self, message, value, charset=None):
        '''ugettext method with default values'''
        if charset:
            self.translations._charset = charset
        tools.ok_(self.translations.ugettext(message) == value)

    def check_ngettext(self, message, value, charset=None):
        if charset:
            self.translations.set_output_charset(charset)
        tools.ok_(self.translations.ngettext(message, 'blank', 1) == value)
        tools.ok_(self.translations.ngettext('blank', message, 2) == value)
        tools.ok_(self.translations.ngettext(message, 'blank', 2) != value)
        tools.ok_(self.translations.ngettext('blank', message, 1) != value)

    def check_lngettext(self, message, value, charset=None, locale='en_US.UTF-8'):
        os.environ['LC_ALL'] = locale
        if charset:
            self.translations.set_output_charset(charset)
        tools.ok_(self.translations.lngettext(message, 'blank', 1) == value)
        tools.ok_(self.translations.lngettext('blank', message, 2) == value)
        tools.ok_(self.translations.lngettext(message, 'blank', 2) != value)
        tools.ok_(self.translations.lngettext('blank', message, 1) != value)

    def check_ungettext(self, message, value, charset=None):
        if charset:
            self.translations._charset = charset
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
