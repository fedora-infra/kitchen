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
        tools.ok_(_.__func__.__name__ == 'ugettext')
        tools.ok_(N_.__func__.__name__ == 'ungettext')

        tools.ok_(_('café') == 'café')
        tools.ok_(_('café') == 'café')
        tools.ok_(N_('café', 'cafés', 1) == 'café')
        tools.ok_(N_('café', 'cafés', 2) == 'cafés')
        tools.ok_(N_('café', 'cafés', 1) == 'café')
        tools.ok_(N_('café', 'cafés', 2) == 'cafés')

    def test_easy_gettext_setup_non_unicode(self):
        '''Test that the easy_gettext_setup function works
        '''
        b_, bN_ = i18n.easy_gettext_setup('foo', localedirs=
                ['%s/data/locale/' % os.path.dirname(__file__)],
                use_unicode=False)
        tools.ok_(isinstance(b_, types.MethodType))
        tools.ok_(isinstance(bN_, types.MethodType))
        tools.ok_(b_.__func__.__name__ == 'lgettext')
        tools.ok_(bN_.__func__.__name__ == 'lngettext')

        tools.ok_(b_('café') == 'café')
        tools.ok_(b_('café') == 'café')
        tools.ok_(bN_('café', 'cafés', 1) == 'café')
        tools.ok_(bN_('café', 'cafés', 2) == 'cafés')
        tools.ok_(bN_('café', 'cafés', 1) == 'café')
        tools.ok_(bN_('café', 'cafés', 2) == 'cafés')

    def test_get_translation_object(self):
        '''Test that the get_translation_object function works
        '''
        translations = i18n.get_translation_object('foo', ['%s/data/locale/' % os.path.dirname(__file__)])
        tools.ok_(translations.__class__==i18n.DummyTranslations)
        tools.assert_raises(IOError, i18n.get_translation_object, 'foo', ['%s/data/locale/' % os.path.dirname(__file__)], fallback=False)

        translations = i18n.get_translation_object('test', ['%s/data/locale/' % os.path.dirname(__file__)])
        tools.ok_(translations.__class__==i18n.NewGNUTranslations)

    def test_get_translation_object_create_fallback(self):
        '''Test get_translation_object creates fallbacks for additional catalogs'''
        translations = i18n.get_translation_object('test',
                ['%s/data/locale' % os.path.dirname(__file__),
                    '%s/data/locale-old' % os.path.dirname(__file__)])
        tools.ok_(translations.__class__==i18n.NewGNUTranslations)
        tools.ok_(translations._fallback.__class__==i18n.NewGNUTranslations)

    def test_get_translation_object_copy(self):
        '''Test get_translation_object shallow copies the message catalog'''
        translations = i18n.get_translation_object('test',
                ['%s/data/locale' % os.path.dirname(__file__),
                    '%s/data/locale-old' % os.path.dirname(__file__)], codeset='utf-8')
        translations.input_charset = 'utf-8'
        translations2 = i18n.get_translation_object('test',
                ['%s/data/locale' % os.path.dirname(__file__),
                    '%s/data/locale-old' % os.path.dirname(__file__)], codeset='latin-1')
        translations2.input_charset = 'latin-1'

        # Test that portions of the translation objects are the same and other
        # portions are different (which is a space optimization so that the
        # translation data isn't in memory multiple times)
        tools.ok_(id(translations._fallback) != id(translations2._fallback))
        tools.ok_(id(translations.output_charset()) != id(translations2.output_charset()))
        tools.ok_(id(translations.input_charset) != id(translations2.input_charset))
        tools.ok_(id(translations.input_charset) != id(translations2.input_charset))
        tools.eq_(id(translations._catalog), id(translations2._catalog))

    def test_get_translation_object_optional_params(self):
        '''Smoketest leaving out optional parameters'''
        translations = i18n.get_translation_object('test')
        tools.ok_(translations.__class__ in (i18n.NewGNUTranslations, i18n.DummyTranslations))

    def test_dummy_translation(self):
        '''Test that we can create a DummyTranslation object
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
                (self.latin1_spanish, self.utf8_mangled_spanish_latin1_as_utf8),
                (self.utf8_japanese, self.utf8_japanese),
                ),
                ( # Second set is with output_charset of latin1 (ISO-8859-1)
                (self.u_ascii, self.b_ascii),
                (self.u_spanish, self.latin1_spanish),
                (self.u_japanese, self.latin1_mangled_japanese_replace_as_latin1),
                (self.b_ascii, self.b_ascii),
                (self.utf8_spanish, self.utf8_spanish),
                (self.latin1_spanish, self.latin1_spanish),
                (self.utf8_japanese, self.utf8_japanese),
                ),
                ( # Third set is with output_charset of C
                (self.u_ascii, self.b_ascii),
                (self.u_spanish, self.ascii_mangled_spanish_as_ascii),
                (self.u_japanese, self.ascii_mangled_japanese_replace_as_latin1),
                (self.b_ascii, self.b_ascii),
                (self.utf8_spanish, self.ascii_mangled_spanish_as_ascii),
                (self.latin1_spanish, self.ascii_twice_mangled_spanish_latin1_as_utf8_as_ascii),
                (self.utf8_japanese, self.ascii_mangled_japanese_replace_as_latin1),
                ),
            ),
            'unicode': (( # First set is with the default charset (utf8)
                (self.u_ascii, self.u_ascii),
                (self.u_spanish, self.u_spanish),
                (self.u_japanese, self.u_japanese),
                (self.b_ascii, self.u_ascii),
                (self.utf8_spanish, self.u_spanish),
                (self.latin1_spanish, self.u_mangled_spanish_latin1_as_utf8), # String is mangled but no exception
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
                (self.utf8_spanish, self.u_mangled_spanish_utf8_as_ascii), # String mangled but no exception
                (self.latin1_spanish, self.u_mangled_spanish_latin1_as_ascii), # String mangled but no exception
                (self.utf8_japanese, self.u_mangled_japanese_utf8_as_ascii), # String mangled but no exception
                ),
            )
    }

    def setUp(self):
        self.translations = i18n.DummyTranslations()

    def check_gettext(self, message, value, charset=None):
        self.translations.set_output_charset(charset)
        tools.eq_(self.translations.gettext(message), value,
                msg='gettext(%s): trans: %s != val: %s (charset=%s)'
                % (repr(message), repr(self.translations.gettext(message)),
                    repr(value), charset))

    def check_lgettext(self, message, value, charset=None,
            locale='en_US.UTF-8'):
        os.environ['LC_ALL'] = locale
        self.translations.set_output_charset(charset)
        tools.eq_(self.translations.lgettext(message), value,
                msg='lgettext(%s): trans: %s != val: %s (charset=%s, locale=%s)'
                % (repr(message), repr(self.translations.lgettext(message)),
                    repr(value), charset, locale))

    # Note: charset has a default value because nose isn't invoking setUp and
    # tearDown each time check_* is run.
    def check_ugettext(self, message, value, charset='utf-8'):
        '''ugettext method with default values'''
        self.translations.input_charset = charset
        tools.eq_(self.translations.ugettext(message), value,
                msg='ugettext(%s): trans: %s != val: %s (charset=%s)'
                % (repr(message), repr(self.translations.ugettext(message)),
                    repr(value), charset))

    def check_ngettext(self, message, value, charset=None):
        self.translations.set_output_charset(charset)
        tools.eq_(self.translations.ngettext(message, 'blank', 1), value)
        tools.eq_(self.translations.ngettext('blank', message, 2), value)
        tools.ok_(self.translations.ngettext(message, 'blank', 2) != value)
        tools.ok_(self.translations.ngettext('blank', message, 1) != value)

    def check_lngettext(self, message, value, charset=None, locale='en_US.UTF-8'):
        os.environ['LC_ALL'] = locale
        self.translations.set_output_charset(charset)
        tools.eq_(self.translations.lngettext(message, 'blank', 1), value,
                msg='lngettext(%s, "blank", 1): trans: %s != val: %s (charset=%s, locale=%s)'
                % (repr(message), repr(self.translations.lngettext(message,
                    'blank', 1)), repr(value), charset, locale))
        tools.eq_(self.translations.lngettext('blank', message, 2), value,
                msg='lngettext("blank", %s, 2): trans: %s != val: %s (charset=%s, locale=%s)'
                % (repr(message), repr(self.translations.lngettext('blank',
                    message, 2)), repr(value), charset, locale))
        tools.ok_(self.translations.lngettext(message, 'blank', 2) != value,
                msg='lngettext(%s, "blank", 2): trans: %s != val: %s (charset=%s, locale=%s)'
                % (repr(message), repr(self.translations.lngettext(message,
                    'blank', 2)), repr(value), charset, locale))
        tools.ok_(self.translations.lngettext('blank', message, 1) != value,
                msg='lngettext("blank", %s, 1): trans: %s != val: %s (charset=%s, locale=%s)'
                % (repr(message), repr(self.translations.lngettext('blank',
                    message, 1)), repr(value), charset, locale))

    # Note: charset has a default value because nose isn't invoking setUp and
    # tearDown each time check_* is run.
    def check_ungettext(self, message, value, charset='utf-8'):
        self.translations.input_charset = charset
        tools.eq_(self.translations.ungettext(message, 'blank', 1), value)
        tools.eq_(self.translations.ungettext('blank', message, 2), value)
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
        tools.eq_(self.translations.gettext(dict(hi='there')), '')
        tools.eq_(self.translations.ngettext(dict(hi='there'), dict(hi='two'), 1), '')
        tools.eq_(self.translations.lgettext(dict(hi='there')), '')
        tools.eq_(self.translations.lngettext(dict(hi='there'), dict(hi='two'), 1), '')
        tools.eq_(self.translations.ugettext(dict(hi='there')), '')
        tools.eq_(self.translations.ungettext(dict(hi='there'), dict(hi='two'), 1), '')


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
        tools.ok_(b_('café') == 'caf\xe9')
        tools.ok_(bN_('café', 'cafés', 1) == 'café')
        tools.ok_(bN_('café', 'cafés', 2) == 'cafés')
        tools.ok_(bN_('café', 'cafés', 1) == 'caf\xe9')
        tools.ok_(bN_('café', 'cafés', 2) == 'caf\xe9s')


class TestNewGNUTranslationsNoMatch(TestDummyTranslations):
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
        tools.ok_(_('Only café in fallback')=='Only café in fallback')

        tools.ok_(_('kitchen sink')=='pia da cozinha')
        tools.ok_(_('くらとみ')=='Kuratomi')
        tools.ok_(_('Kuratomi')=='くらとみ')
        tools.ok_(_('Only café in fallback')=='Only café in fallback')

    def test_ngettext(self):
        _ = self.translations.ngettext
        tools.ok_(_('1 lemon', '4 lemons', 1)=='一 limão')
        tools.ok_(_('一 limão', '四 limões', 1)=='1 lemon')
        tools.ok_(_('1 lemon', '4 lemons', 1)=='一 limão')
        tools.ok_(_('一 limão', '四 limões', 1)=='1 lemon')

        tools.ok_(_('1 lemon', '4 lemons', 2)=='四 limões')
        tools.ok_(_('一 limão', '四 limões', 2)=='4 lemons')
        tools.ok_(_('1 lemon', '4 lemons', 2)=='四 limões')
        tools.ok_(_('一 limão', '四 limões', 2)=='4 lemons')

    def test_lgettext(self):
        _ = self.translations.lgettext
        tools.ok_(_('kitchen sink')=='pia da cozinha')
        tools.ok_(_('Kuratomi')=='くらとみ')
        tools.ok_(_('くらとみ')=='Kuratomi')
        tools.ok_(_('Only café in fallback')=='Only café in fallback')

        tools.ok_(_('kitchen sink')=='pia da cozinha')
        tools.ok_(_('くらとみ')=='Kuratomi')
        tools.ok_(_('Kuratomi')=='くらとみ')
        tools.ok_(_('Only café in fallback')=='Only café in fallback')

    def test_lngettext(self):
        _ = self.translations.lngettext
        tools.ok_(_('1 lemon', '4 lemons', 1)=='一 limão')
        tools.ok_(_('一 limão', '四 limões', 1)=='1 lemon')
        tools.ok_(_('1 lemon', '4 lemons', 1)=='一 limão')
        tools.ok_(_('一 limão', '四 limões', 1)=='1 lemon')

        tools.ok_(_('1 lemon', '4 lemons', 2)=='四 limões')
        tools.ok_(_('一 limão', '四 limões', 2)=='4 lemons')
        tools.ok_(_('1 lemon', '4 lemons', 2)=='四 limões')
        tools.ok_(_('一 limão', '四 limões', 2)=='4 lemons')

    def test_ugettext(self):
        _ = self.translations.ugettext
        tools.ok_(_('kitchen sink')=='pia da cozinha')
        tools.ok_(_('Kuratomi')=='くらとみ')
        tools.ok_(_('くらとみ')=='Kuratomi')
        tools.ok_(_('Only café in fallback')=='Only café in fallback')

        tools.ok_(_('kitchen sink')=='pia da cozinha')
        tools.ok_(_('くらとみ')=='Kuratomi')
        tools.ok_(_('Kuratomi')=='くらとみ')
        tools.ok_(_('Only café in fallback')=='Only café in fallback')

    def test_ungettext(self):
        _ = self.translations.ungettext
        tools.ok_(_('1 lemon', '4 lemons', 1)=='一 limão')
        tools.ok_(_('一 limão', '四 limões', 1)=='1 lemon')
        tools.ok_(_('1 lemon', '4 lemons', 1)=='一 limão')
        tools.ok_(_('一 limão', '四 limões', 1)=='1 lemon')

        tools.ok_(_('1 lemon', '4 lemons', 2)=='四 limões')
        tools.ok_(_('一 limão', '四 limões', 2)=='4 lemons')
        tools.ok_(_('1 lemon', '4 lemons', 2)=='四 limões')
        tools.ok_(_('一 limão', '四 limões', 2)=='4 lemons')


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
        tools.eq_(_('kitchen sink'), 'pia da cozinha')
        tools.eq_(_('Kuratomi'), '????')
        tools.eq_(_('くらとみ'), 'Kuratomi')
        # The following returns utf-8 because latin-1 can hold all of the
        # bytes that are present in utf-8 encodings.  Therefore, we cannot
        # tell that we should reencode the string.  This will be displayed as
        # mangled text if used in a program
        tools.eq_(_('Only café in fallback'), 'Only caf\xc3\xa9 in fallback')

        tools.eq_(_('kitchen sink'), 'pia da cozinha')
        tools.eq_(_('くらとみ'), 'Kuratomi')
        tools.eq_(_('Kuratomi'), '????')
        tools.eq_(_('Only café in fallback'), 'Only caf\xe9 in fallback')

    def test_lngettext(self):
        _ = self.translations.lngettext
        tools.ok_(_('1 lemon', '4 lemons', 1)=='? lim\xe3o')
        tools.ok_(_('一 limão', '四 limões', 1)=='1 lemon')
        tools.ok_(_('1 lemon', '4 lemons', 1)=='? lim\xe3o')
        tools.ok_(_('一 limão', '四 limões', 1)=='1 lemon')

        tools.ok_(_('1 lemon', '4 lemons', 2)=='? lim\xf5es')
        tools.ok_(_('一 limão', '四 limões', 2)=='4 lemons')
        tools.ok_(_('1 lemon', '4 lemons', 2)=='? lim\xf5es')
        tools.ok_(_('一 limão', '四 limões', 2)=='4 lemons')


class TestFallbackNewGNUTranslationsNoMatch(TestDummyTranslations):
    def setUp(self):
        self.old_LC_ALL = os.environ.get('LC_ALL', None)
        os.environ['LC_ALL'] = 'pt_BR.utf8'
        self.translations = i18n.get_translation_object('test',
                ['%s/data/locale/' % os.path.dirname(__file__),
                    '%s/data/locale-old' % os.path.dirname(__file__)])

    def tearDown(self):
        if self.old_LC_ALL:
            os.environ['LC_ALL'] = self.old_LC_ALL
        else:
            del(os.environ['LC_ALL'])


class TestFallbackNewGNURealTranslations_UTF8(unittest.TestCase):
    def setUp(self):
        self.old_LC_ALL = os.environ.get('LC_ALL', None)
        os.environ['LC_ALL'] = 'pt_BR.UTF8'
        self.translations = i18n.get_translation_object('test',
                ['%s/data/locale/' % os.path.dirname(__file__),
                    '%s/data/locale-old' % os.path.dirname(__file__)])

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
        tools.ok_(_('Only café in fallback')=='Yes, only caf\xc3\xa9 in fallback')

        tools.ok_(_('kitchen sink')=='pia da cozinha')
        tools.ok_(_('くらとみ')=='Kuratomi')
        tools.ok_(_('Kuratomi')=='くらとみ')
        tools.ok_(_('Only café in fallback')=='Yes, only caf\xc3\xa9 in fallback')

    def test_ngettext(self):
        _ = self.translations.ngettext
        tools.ok_(_('1 lemon', '4 lemons', 1)=='一 limão')
        tools.ok_(_('一 limão', '四 limões', 1)=='1 lemon')
        tools.ok_(_('1 lemon', '4 lemons', 1)=='一 limão')
        tools.ok_(_('一 limão', '四 limões', 1)=='1 lemon')

        tools.ok_(_('1 lemon', '4 lemons', 2)=='四 limões')
        tools.ok_(_('一 limão', '四 limões', 2)=='4 lemons')
        tools.ok_(_('1 lemon', '4 lemons', 2)=='四 limões')
        tools.ok_(_('一 limão', '四 limões', 2)=='4 lemons')

    def test_lgettext(self):
        _ = self.translations.lgettext
        tools.eq_(_('kitchen sink'), 'pia da cozinha')
        tools.ok_(_('Kuratomi')=='くらとみ')
        tools.ok_(_('くらとみ')=='Kuratomi')
        tools.ok_(_('Only café in fallback')=='Yes, only caf\xc3\xa9 in fallback')

        tools.ok_(_('kitchen sink')=='pia da cozinha')
        tools.ok_(_('くらとみ')=='Kuratomi')
        tools.ok_(_('Kuratomi')=='くらとみ')
        tools.ok_(_('Only café in fallback')=='Yes, only caf\xc3\xa9 in fallback')

    def test_lngettext(self):
        _ = self.translations.lngettext
        tools.ok_(_('1 lemon', '4 lemons', 1)=='一 limão')
        tools.ok_(_('一 limão', '四 limões', 1)=='1 lemon')
        tools.ok_(_('1 lemon', '4 lemons', 1)=='一 limão')
        tools.ok_(_('一 limão', '四 limões', 1)=='1 lemon')

        tools.ok_(_('1 lemon', '4 lemons', 2)=='四 limões')
        tools.ok_(_('一 limão', '四 limões', 2)=='4 lemons')
        tools.ok_(_('1 lemon', '4 lemons', 2)=='四 limões')
        tools.ok_(_('一 limão', '四 limões', 2)=='4 lemons')

    def test_ugettext(self):
        _ = self.translations.ugettext
        tools.ok_(_('kitchen sink')=='pia da cozinha')
        tools.ok_(_('Kuratomi')=='くらとみ')
        tools.ok_(_('くらとみ')=='Kuratomi')
        tools.ok_(_('Only café in fallback')=='Yes, only caf\xe9 in fallback')

        tools.ok_(_('kitchen sink')=='pia da cozinha')
        tools.ok_(_('くらとみ')=='Kuratomi')
        tools.ok_(_('Kuratomi')=='くらとみ')
        tools.ok_(_('Only café in fallback')=='Yes, only caf\xe9 in fallback')

    def test_ungettext(self):
        _ = self.translations.ungettext
        tools.ok_(_('1 lemon', '4 lemons', 1)=='一 limão')
        tools.ok_(_('一 limão', '四 limões', 1)=='1 lemon')
        tools.ok_(_('1 lemon', '4 lemons', 1)=='一 limão')
        tools.ok_(_('一 limão', '四 limões', 1)=='1 lemon')

        tools.ok_(_('1 lemon', '4 lemons', 2)=='四 limões')
        tools.ok_(_('一 limão', '四 limões', 2)=='4 lemons')
        tools.ok_(_('1 lemon', '4 lemons', 2)=='四 limões')
        tools.ok_(_('一 limão', '四 limões', 2)=='4 lemons')


class TestFallbackNewGNURealTranslations_Latin1(unittest.TestCase):
    def setUp(self):
        self.old_LC_ALL = os.environ.get('LC_ALL', None)
        os.environ['LC_ALL'] = 'pt_BR.ISO8859-1'
        self.translations = i18n.get_translation_object('test',
                ['%s/data/locale/' % os.path.dirname(__file__),
                    '%s/data/locale-old' % os.path.dirname(__file__)])

    def tearDown(self):
        if self.old_LC_ALL:
            os.environ['LC_ALL'] = self.old_LC_ALL
        else:
            del(os.environ['LC_ALL'])

    def test_gettext(self):
        _ = self.translations.gettext
        tools.ok_(_(b'kitchen sink')=='pia da cozinha'.encode('utf-8'))
        tools.ok_(_(b'Kuratomi')=='くらとみ'.encode('utf-8'))
        tools.ok_(_('くらとみ'.encode('utf-8'))==b'Kuratomi')
        tools.ok_(_('Only café in fallback'.encode('utf-8'))=='Yes, only café in fallback'.encode('utf-8'))
        tools.eq_(_('café not matched in catalogs'.encode('utf-8')), 'café not matched in catalogs'.encode('utf-8'))

        tools.ok_(_('kitchen sink')=='pia da cozinha'.encode('utf-8'))
        tools.ok_(_('くらとみ')==b'Kuratomi')
        tools.ok_(_('Kuratomi')=='くらとみ'.encode('utf-8'))
        tools.ok_(_('Only café in fallback')=='Yes, only café in fallback'.encode('utf-'))
        tools.eq_(_('café not matched in catalogs'), 'café not matched in catalogs'.encode('utf-8'))

    def test_ngettext(self):
        _ = self.translations.ngettext
        tools.ok_(_(b'1 lemon', b'4 lemons', 1)=='一 limão'.encode('utf-8'))
        tools.ok_(_('一 limão'.encode('utf-8'), '四 limões'.encode('utf-8'), 1)==b'1 lemon')
        tools.ok_(_('1 lemon', '4 lemons', 1)=='一 limão'.encode('utf-8'))
        tools.ok_(_('一 limão', '四 limões', 1)==b'1 lemon')
        tools.eq_(_('café not matched in catalogs', 'throwaway', 1), 'café not matched in catalogs'.encode('utf-8'))

        tools.ok_(_(b'1 lemon', b'4 lemons', 2)=='四 limões'.encode('utf-8'))
        tools.ok_(_('一 limão'.encode('utf-8'), '四 limões'.encode('utf-8'), 2)==b'4 lemons')
        tools.ok_(_('1 lemon', '4 lemons', 2)=='四 limões'.encode('utf-8'))
        tools.ok_(_('一 limão', '四 limões', 2)==b'4 lemons')
        tools.eq_(_('café not matched in catalogs', 'throwaway', 1), 'café not matched in catalogs'.encode('utf-8'))

    def test_lgettext(self):
        _ = self.translations.lgettext
        tools.eq_(_(b'kitchen sink'), 'pia da cozinha'.encode('latin-1'))
        tools.eq_(_(b'Kuratomi'), b'????')
        tools.eq_(_('くらとみ'.encode('utf-8')), b'Kuratomi')
        tools.eq_(_('Only café in fallback'.encode('utf-8')), 'Yes, only café in fallback'.encode('latin-1'))
        # This unfortunately does not encode to proper latin-1 because:
        # any byte is valid in latin-1 so there's no way to know that what
        # we're given in the string is really utf-8
        tools.eq_(_('café not matched in catalogs'.encode('utf-8')), 'café not matched in catalogs'.encode('utf-8'))

        tools.eq_(_('kitchen sink'), 'pia da cozinha'.encode('latin-1'))
        tools.eq_(_('くらとみ'), b'Kuratomi')
        tools.eq_(_('Kuratomi'), b'????')
        tools.eq_(_('Only café in fallback'), 'Yes, only café in fallback'.encode('latin-1'))
        tools.eq_(_('café not matched in catalogs'), 'café not matched in catalogs'.encode('latin-1'))

    def test_lngettext(self):
        _ = self.translations.lngettext
        tools.eq_(_(b'1 lemon', b'4 lemons', 1), '一 limão'.encode('latin1', 'replace'))
        tools.eq_(_('一 limão'.encode('utf-8'), '四 limões'.encode('utf-8'), 1), b'1 lemon')
        tools.eq_(_('1 lemon', '4 lemons', 1), '一 limão'.encode('latin1', 'replace'))
        tools.eq_(_('一 limão', '四 limões', 1), b'1 lemon')
        # This unfortunately does not encode to proper latin-1 because:
        # any byte is valid in latin-1 so there's no way to know that what
        # we're given in the string is really utf-8
        tools.eq_(_('café not matched in catalogs'.encode('utf-8'), b'throwaway', 1), 'café not matched in catalogs'.encode('utf-8'))

        tools.eq_(_(b'1 lemon', b'4 lemons', 2), '四 limões'.encode('latin1', 'replace'))
        tools.eq_(_('一 limão'.encode('utf-8'), '四 limões'.encode('utf-8'), 2), b'4 lemons')
        tools.eq_(_('1 lemon', '4 lemons', 2), '四 limões'.encode('latin1', 'replace'))
        tools.eq_(_('一 limão', '四 limões', 2), b'4 lemons')
        tools.eq_(_('café not matched in catalogs', 'throwaway', 1), 'café not matched in catalogs'.encode('latin-1'))

    def test_ugettext(self):
        _ = self.translations.ugettext
        tools.ok_(_(b'kitchen sink')=='pia da cozinha')
        tools.ok_(_(b'Kuratomi')=='くらとみ')
        tools.ok_(_('くらとみ'.encode('utf-8'))=='Kuratomi')
        tools.ok_(_('Only café in fallback'.encode('utf-8'))=='Yes, only café in fallback')
        tools.eq_(_('café not matched in catalogs'.encode('utf-8')), 'café not matched in catalogs')

        tools.ok_(_('kitchen sink')=='pia da cozinha')
        tools.ok_(_('くらとみ')=='Kuratomi')
        tools.ok_(_('Kuratomi')=='くらとみ')
        tools.ok_(_('Only café in fallback')=='Yes, only café in fallback')
        tools.eq_(_('café not matched in catalogs'), 'café not matched in catalogs')

    def test_ungettext(self):
        _ = self.translations.ungettext
        tools.ok_(_('1 lemon', '4 lemons', 1)=='一 limão')
        tools.ok_(_('一 limão', '四 limões', 1)=='1 lemon')
        tools.ok_(_('1 lemon', '4 lemons', 1)=='一 limão')
        tools.ok_(_('一 limão', '四 limões', 1)=='1 lemon')

        tools.ok_(_('1 lemon', '4 lemons', 2)=='四 limões')
        tools.ok_(_('一 limão', '四 limões', 2)=='4 lemons')
        tools.ok_(_('1 lemon', '4 lemons', 2)=='四 limões')
        tools.ok_(_('一 limão', '四 limões', 2)=='4 lemons')

        tools.eq_(_('café not matched in catalogs'.encode('utf-8'), 'throwaway', 1), 'café not matched in catalogs')
        tools.eq_(_('café not matched in catalogs', 'throwaway', 1), 'café not matched in catalogs')


class TestFallback(unittest.TestCase):
    def setUp(self):
        self.old_LC_ALL = os.environ.get('LC_ALL', None)
        os.environ['LC_ALL'] = 'pt_BR.ISO8859-1'
        self.gtranslations = i18n.get_translation_object('test',
                ['%s/data/locale/' % os.path.dirname(__file__),
                    '%s/data/locale-old' % os.path.dirname(__file__)])
        self.gtranslations.add_fallback(object())
        self.dtranslations = i18n.get_translation_object('nonexistent',
                ['%s/data/locale/' % os.path.dirname(__file__),
                    '%s/data/locale-old' % os.path.dirname(__file__)])
        self.dtranslations.add_fallback(object())


    def tearDown(self):
        if self.old_LC_ALL:
            os.environ['LC_ALL'] = self.old_LC_ALL
        else:
            del(os.environ['LC_ALL'])

    def test_invalid_fallback_no_raise(self):
        '''Test when we have an invalid fallback that it does not raise.'''
        utf8_cafe = 'café'.encode('utf-8')
        tools.eq_(self.gtranslations.gettext('café'), utf8_cafe)
        tools.eq_(self.gtranslations.ugettext('café'), 'café')
        tools.eq_(self.gtranslations.lgettext('café'), utf8_cafe)

        tools.eq_(self.gtranslations.ngettext('café', 'cde', 1), utf8_cafe)
        tools.eq_(self.gtranslations.ungettext('café', 'cde', 1), 'café')
        tools.eq_(self.gtranslations.lngettext('café', 'cde', 1), utf8_cafe)

        tools.eq_(self.dtranslations.gettext('café'), utf8_cafe)
        tools.eq_(self.dtranslations.ugettext('café'), 'café')
        tools.eq_(self.dtranslations.lgettext('café'), utf8_cafe)

        tools.eq_(self.dtranslations.ngettext('café', 'cde', 1), utf8_cafe)
        tools.eq_(self.dtranslations.ungettext('café', 'cde', 1), 'café')
        tools.eq_(self.dtranslations.lngettext('café', 'cde', 1), utf8_cafe)


class TestDefaultLocaleDir(unittest.TestCase):
    def setUp(self):
        self.old_LC_ALL = os.environ.get('LC_ALL', None)
        os.environ['LC_ALL'] = 'pt_BR.UTF8'
        self.old_DEFAULT_LOCALEDIRS = i18n._DEFAULT_LOCALEDIR
        i18n._DEFAULT_LOCALEDIR = '%s/data/locale/' % os.path.dirname(__file__)
        self.translations = i18n.get_translation_object('test')

    def tearDown(self):
        if self.old_LC_ALL:
            os.environ['LC_ALL'] = self.old_LC_ALL
        else:
            del(os.environ['LC_ALL'])
        if self.old_DEFAULT_LOCALEDIRS:
            i18n._DEFAULT_LOCALEDIR = self.old_DEFAULT_LOCALEDIRS

    def test_gettext(self):
        _ = self.translations.gettext
        tools.eq_(_('kitchen sink'), 'pia da cozinha')
        tools.eq_(_('Kuratomi'), 'くらとみ')
        tools.eq_(_('くらとみ'), 'Kuratomi')
        tools.eq_(_('Only café in fallback'), 'Only café in fallback')

        tools.eq_(_('kitchen sink'), 'pia da cozinha')
        tools.eq_(_('くらとみ'), 'Kuratomi')
        tools.eq_(_('Kuratomi'), 'くらとみ')
        tools.eq_(_('Only café in fallback'), 'Only café in fallback')


