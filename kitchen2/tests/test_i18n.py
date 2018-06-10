# -*- coding: utf-8 -*-
#
import unittest
from nose import tools

import os
import types

from kitchen import i18n

import base_classes

class TestI18N_UTF8(unittest.TestCase, base_classes.UnicodeTestData):
    def setUp(self):
        self.old_LC_ALL = os.environ.get('LC_ALL', None)
        os.environ['LC_ALL'] = 'pt_BR.utf8'

        self.old_LANGUAGE = os.environ.pop('LANGUAGE', None)

    def tearDown(self):
        if self.old_LC_ALL:
            os.environ['LC_ALL'] = self.old_LC_ALL
        else:
            del(os.environ['LC_ALL'])

        if self.old_LANGUAGE:
            os.environ['LANGUAGE'] = self.old_LANGUAGE

    def test_easy_gettext_setup(self):
        '''Test that the easy_gettext_setup function works
        '''
        _, N_ = i18n.easy_gettext_setup('foo', localedirs=
                ['%s/data/locale/' % os.path.dirname(__file__)])
        tools.assert_true(isinstance(_, types.MethodType))
        tools.assert_true(isinstance(N_, types.MethodType))
        tools.eq_(_.__name__, '_ugettext')
        tools.eq_(N_.__name__, '_ungettext')

        tools.eq_(_(self.utf8_spanish), self.u_spanish)
        tools.eq_(_(self.u_spanish), self.u_spanish)
        tools.eq_(N_(self.utf8_limao, self.utf8_limoes, 1), self.u_limao)
        tools.eq_(N_(self.utf8_limao, self.utf8_limoes, 2), self.u_limoes)
        tools.eq_(N_(self.u_limao, self.u_limoes, 1), self.u_limao)
        tools.eq_(N_(self.u_limao, self.u_limoes, 2), self.u_limoes)

    def test_easy_gettext_setup_non_unicode(self):
        '''Test that the easy_gettext_setup function works
        '''
        b_, bN_ = i18n.easy_gettext_setup('foo', localedirs=
                ['%s/data/locale/' % os.path.dirname(__file__)],
                use_unicode=False)
        tools.assert_true(isinstance(b_, types.MethodType))
        tools.assert_true(isinstance(bN_, types.MethodType))
        tools.eq_(b_.__name__, '_lgettext')
        tools.eq_(bN_.__name__, '_lngettext')

        tools.eq_(b_(self.utf8_spanish), self.utf8_spanish)
        tools.eq_(b_(self.u_spanish), self.utf8_spanish)
        tools.eq_(bN_(self.utf8_limao, self.utf8_limoes, 1), self.utf8_limao)
        tools.eq_(bN_(self.utf8_limao, self.utf8_limoes, 2), self.utf8_limoes)
        tools.eq_(bN_(self.u_limao, self.u_limoes, 1), self.utf8_limao)
        tools.eq_(bN_(self.u_limao, self.u_limoes, 2), self.utf8_limoes)

    def test_get_translation_object(self):
        '''Test that the get_translation_object function works
        '''
        translations = i18n.get_translation_object('foo', ['%s/data/locale/' % os.path.dirname(__file__)])
        tools.eq_(translations.__class__, i18n.DummyTranslations)
        tools.assert_raises(IOError, i18n.get_translation_object, 'foo', ['%s/data/locale/' % os.path.dirname(__file__)], fallback=False)

        translations = i18n.get_translation_object('test', ['%s/data/locale/' % os.path.dirname(__file__)])
        tools.eq_(translations.__class__, i18n.NewGNUTranslations)

    def test_get_translation_object_create_fallback(self):
        '''Test get_translation_object creates fallbacks for additional catalogs'''
        translations = i18n.get_translation_object('test',
                ['%s/data/locale' % os.path.dirname(__file__),
                    '%s/data/locale-old' % os.path.dirname(__file__)])
        tools.eq_(translations.__class__, i18n.NewGNUTranslations)
        tools.eq_(translations._fallback.__class__, i18n.NewGNUTranslations)

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
        tools.assert_not_equal(id(translations._fallback), id(translations2._fallback))
        tools.assert_not_equal(id(translations.output_charset()), id(translations2.output_charset()))
        tools.assert_not_equal(id(translations.input_charset), id(translations2.input_charset))
        tools.assert_not_equal(id(translations.input_charset), id(translations2.input_charset))
        tools.eq_(id(translations._catalog), id(translations2._catalog))

    def test_get_translation_object_optional_params(self):
        '''Smoketest leaving out optional parameters'''
        translations = i18n.get_translation_object('test')
        tools.assert_true(translations.__class__ in (i18n.NewGNUTranslations, i18n.DummyTranslations))

    def test_get_translation_object_python2_api_default(self):
        '''Smoketest that python2_api default value yields the python2 functions'''
        # Default
        translations = i18n.get_translation_object('test',
                ['%s/data/locale' % os.path.dirname(__file__),
                    '%s/data/locale-old' % os.path.dirname(__file__)], codeset='utf-8')
        translations.input_charset = 'utf-8'
        tools.eq_(translations.gettext.__name__, '_gettext')
        tools.eq_(translations.lgettext.__name__, '_lgettext')
        tools.eq_(translations.ugettext.__name__, '_ugettext')
        tools.eq_(translations.ngettext.__name__, '_ngettext')
        tools.eq_(translations.lngettext.__name__, '_lngettext')
        tools.eq_(translations.ungettext.__name__, '_ungettext')

    def test_get_translation_object_python2_api_true(self):
        '''Smoketest that setting python2_api true yields the python2 functions'''
        # Default
        translations = i18n.get_translation_object('test',
                ['%s/data/locale' % os.path.dirname(__file__),
                    '%s/data/locale-old' % os.path.dirname(__file__)], codeset='utf-8',
                python2_api=True)
        translations.input_charset = 'utf-8'
        tools.eq_(translations.gettext.__name__, '_gettext')
        tools.eq_(translations.lgettext.__name__, '_lgettext')
        tools.eq_(translations.ugettext.__name__, '_ugettext')
        tools.eq_(translations.ngettext.__name__, '_ngettext')
        tools.eq_(translations.lngettext.__name__, '_lngettext')
        tools.eq_(translations.ungettext.__name__, '_ungettext')

    def test_get_translation_object_python2_api_false(self):
        '''Smoketest that setting python2_api false yields the python3 functions'''
        # Default
        translations = i18n.get_translation_object('test',
                ['%s/data/locale' % os.path.dirname(__file__),
                    '%s/data/locale-old' % os.path.dirname(__file__)], codeset='utf-8',
                python2_api=False)
        translations.input_charset = 'utf-8'
        tools.eq_(translations.gettext.__name__, '_ugettext')
        tools.eq_(translations.lgettext.__name__, '_lgettext')
        tools.eq_(translations.ngettext.__name__, '_ungettext')
        tools.eq_(translations.lngettext.__name__, '_lngettext')

        tools.assert_raises(AttributeError, translations.ugettext, 'message')
        tools.assert_raises(AttributeError, translations.ungettext, 'message1', 'message2')

    def test_dummy_translation(self):
        '''Test that we can create a DummyTranslation object
        '''
        tools.assert_true(isinstance(i18n.DummyTranslations(), i18n.DummyTranslations))

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
        tools.assert_not_equal(self.translations.ngettext(message, 'blank', 2), value)
        tools.assert_not_equal(self.translations.ngettext('blank', message, 1), value)

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
        tools.assert_not_equal(self.translations.lngettext(message, 'blank', 2), value,
                msg='lngettext(%s, "blank", 2): trans: %s, val: %s (charset=%s, locale=%s)'
                % (repr(message), repr(self.translations.lngettext(message,
                    'blank', 2)), repr(value), charset, locale))
        tools.assert_not_equal(self.translations.lngettext('blank', message, 1), value,
                msg='lngettext("blank", %s, 1): trans: %s != val: %s (charset=%s, locale=%s)'
                % (repr(message), repr(self.translations.lngettext('blank',
                    message, 1)), repr(value), charset, locale))

    # Note: charset has a default value because nose isn't invoking setUp and
    # tearDown each time check_* is run.
    def check_ungettext(self, message, value, charset='utf-8'):
        self.translations.input_charset = charset
        tools.eq_(self.translations.ungettext(message, 'blank', 1), value)
        tools.eq_(self.translations.ungettext('blank', message, 2), value)
        tools.assert_not_equal(self.translations.ungettext(message, 'blank', 2), value)
        tools.assert_not_equal(self.translations.ungettext('blank', message, 1), value)

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
        tools.eq_(self.translations.gettext(dict(hi='there')), self.b_empty_string)
        tools.eq_(self.translations.ngettext(dict(hi='there'), dict(hi='two'), 1), self.b_empty_string)
        tools.eq_(self.translations.lgettext(dict(hi='there')), self.b_empty_string)
        tools.eq_(self.translations.lngettext(dict(hi='there'), dict(hi='two'), 1), self.b_empty_string)
        tools.eq_(self.translations.ugettext(dict(hi='there')), self.u_empty_string)
        tools.eq_(self.translations.ungettext(dict(hi='there'), dict(hi='two'), 1), self.u_empty_string)


class TestI18N_Latin1(unittest.TestCase, base_classes.UnicodeTestData):
    def setUp(self):
        self.old_LC_ALL = os.environ.get('LC_ALL', None)
        os.environ['LC_ALL'] = 'pt_BR.iso88591'

        self.old_LANGUAGE = os.environ.pop('LANGUAGE', None)

    def tearDown(self):
        if self.old_LC_ALL:
            os.environ['LC_ALL'] = self.old_LC_ALL
        else:
            del(os.environ['LC_ALL'])

        if self.old_LANGUAGE:
            os.environ['LANGUAGE'] = self.old_LANGUAGE

    def test_easy_gettext_setup_non_unicode(self):
        '''Test that the easy_gettext_setup function works
        '''
        b_, bN_ = i18n.easy_gettext_setup('foo', localedirs=
                ['%s/data/locale/' % os.path.dirname(__file__)],
                use_unicode=False)

        tools.eq_(b_(self.utf8_spanish), self.utf8_spanish)
        tools.eq_(b_(self.u_spanish), self.latin1_spanish)
        tools.eq_(bN_(self.utf8_limao, self.utf8_limoes, 1), self.utf8_limao)
        tools.eq_(bN_(self.utf8_limao, self.utf8_limoes, 2), self.utf8_limoes)
        tools.eq_(bN_(self.u_limao, self.u_limoes, 1), self.latin1_limao)
        tools.eq_(bN_(self.u_limao, self.u_limoes, 2), self.latin1_limoes)


class TestNewGNUTranslationsNoMatch(TestDummyTranslations):
    def setUp(self):
        self.old_LC_ALL = os.environ.get('LC_ALL', None)
        os.environ['LC_ALL'] = 'pt_BR.utf8'

        self.old_LANGUAGE = os.environ.pop('LANGUAGE', None)

        self.translations = i18n.get_translation_object('test', ['%s/data/locale/' % os.path.dirname(__file__)])

    def tearDown(self):
        if self.old_LC_ALL:
            os.environ['LC_ALL'] = self.old_LC_ALL
        else:
            del(os.environ['LC_ALL'])

        if self.old_LANGUAGE:
            os.environ['LANGUAGE'] = self.old_LANGUAGE


class TestNewGNURealTranslations_UTF8(unittest.TestCase, base_classes.UnicodeTestData):
    def setUp(self):
        self.old_LC_ALL = os.environ.get('LC_ALL', None)
        os.environ['LC_ALL'] = 'pt_BR.utf8'

        self.old_LANGUAGE = os.environ.pop('LANGUAGE', None)

        self.translations = i18n.get_translation_object('test', ['%s/data/locale/' % os.path.dirname(__file__)])

    def tearDown(self):
        if self.old_LC_ALL:
            os.environ['LC_ALL'] = self.old_LC_ALL
        else:
            del(os.environ['LC_ALL'])

        if self.old_LANGUAGE:
            os.environ['LANGUAGE'] = self.old_LANGUAGE

    def test_gettext(self):
        _ = self.translations.gettext
        tools.eq_(_(self.utf8_kitchen), self.utf8_pt_kitchen)
        tools.eq_(_(self.utf8_ja_kuratomi), self.utf8_kuratomi)
        tools.eq_(_(self.utf8_kuratomi), self.utf8_ja_kuratomi)
        # This is not translated to utf8_yes_in_fallback because this test is
        # without the fallback message catalog
        tools.eq_(_(self.utf8_in_fallback), self.utf8_in_fallback)
        tools.eq_(_(self.utf8_not_in_catalog), self.utf8_not_in_catalog)

        tools.eq_(_(self.u_kitchen), self.utf8_pt_kitchen)
        tools.eq_(_(self.u_ja_kuratomi), self.utf8_kuratomi)
        tools.eq_(_(self.u_kuratomi), self.utf8_ja_kuratomi)
        # This is not translated to utf8_yes_in_fallback because this test is
        # without the fallback message catalog
        tools.eq_(_(self.u_in_fallback), self.utf8_in_fallback)
        tools.eq_(_(self.u_not_in_catalog), self.utf8_not_in_catalog)

    def test_ngettext(self):
        _ = self.translations.ngettext
        tools.eq_(_(self.utf8_lemon, self.utf8_lemons, 1), self.utf8_limao)
        tools.eq_(_(self.utf8_limao, self.utf8_limoes, 1), self.utf8_lemon)
        tools.eq_(_(self.u_lemon, self.u_lemons, 1), self.utf8_limao)
        tools.eq_(_(self.u_limao, self.u_limoes, 1), self.utf8_lemon)

        tools.eq_(_(self.utf8_lemon, self.utf8_lemons, 2), self.utf8_limoes)
        tools.eq_(_(self.utf8_limao, self.utf8_limoes, 2), self.utf8_lemons)
        tools.eq_(_(self.u_lemon, self.u_lemons, 2), self.utf8_limoes)
        tools.eq_(_(self.u_limao, self.u_limoes, 2), self.utf8_lemons)

        tools.eq_(_(self.utf8_not_in_catalog, 'throwaway', 1), self.utf8_not_in_catalog)
        tools.eq_(_(self.u_not_in_catalog, 'throwaway', 1), self.utf8_not_in_catalog)


    def test_lgettext(self):
        _ = self.translations.lgettext
        tools.eq_(_(self.utf8_kitchen), self.utf8_pt_kitchen)
        tools.eq_(_(self.utf8_ja_kuratomi), self.utf8_kuratomi)
        tools.eq_(_(self.utf8_kuratomi), self.utf8_ja_kuratomi)
        # This is not translated to utf8_yes_in_fallback because this test is
        # without the fallback message catalog
        tools.eq_(_(self.utf8_in_fallback), self.utf8_in_fallback)
        tools.eq_(_(self.utf8_not_in_catalog), self.utf8_not_in_catalog)

        tools.eq_(_(self.u_kitchen), self.utf8_pt_kitchen)
        tools.eq_(_(self.u_ja_kuratomi), self.utf8_kuratomi)
        tools.eq_(_(self.u_kuratomi), self.utf8_ja_kuratomi)
        # This is not translated to utf8_yes_in_fallback because this test is
        # without the fallback message catalog
        tools.eq_(_(self.u_in_fallback), self.utf8_in_fallback)
        tools.eq_(_(self.u_not_in_catalog), self.utf8_not_in_catalog)

    def test_lngettext(self):
        _ = self.translations.lngettext
        tools.eq_(_(self.utf8_lemon, self.utf8_lemons, 1), self.utf8_limao)
        tools.eq_(_(self.utf8_limao, self.utf8_limoes, 1), self.utf8_lemon)
        tools.eq_(_(self.u_lemon, self.u_lemons, 1), self.utf8_limao)
        tools.eq_(_(self.u_limao, self.u_limoes, 1), self.utf8_lemon)

        tools.eq_(_(self.utf8_lemon, self.utf8_lemons, 2), self.utf8_limoes)
        tools.eq_(_(self.utf8_limao, self.utf8_limoes, 2), self.utf8_lemons)
        tools.eq_(_(self.u_lemon, self.u_lemons, 2), self.utf8_limoes)
        tools.eq_(_(self.u_limao, self.u_limoes, 2), self.utf8_lemons)

        tools.eq_(_(self.utf8_not_in_catalog, 'throwaway', 1), self.utf8_not_in_catalog)
        tools.eq_(_(self.u_not_in_catalog, 'throwaway', 1), self.utf8_not_in_catalog)


    def test_ugettext(self):
        _ = self.translations.ugettext
        tools.eq_(_(self.utf8_kitchen), self.u_pt_kitchen)
        tools.eq_(_(self.utf8_ja_kuratomi), self.u_kuratomi)
        tools.eq_(_(self.utf8_kuratomi), self.u_ja_kuratomi)
        # This is not translated to utf8_yes_in_fallback because this test is
        # without the fallback message catalog
        tools.eq_(_(self.utf8_in_fallback), self.u_in_fallback)
        tools.eq_(_(self.utf8_not_in_catalog), self.u_not_in_catalog)

        tools.eq_(_(self.u_kitchen), self.u_pt_kitchen)
        tools.eq_(_(self.u_ja_kuratomi), self.u_kuratomi)
        tools.eq_(_(self.u_kuratomi), self.u_ja_kuratomi)
        # This is not translated to utf8_yes_in_fallback because this test is
        # without the fallback message catalog
        tools.eq_(_(self.u_in_fallback), self.u_in_fallback)
        tools.eq_(_(self.u_not_in_catalog), self.u_not_in_catalog)

    def test_ungettext(self):
        _ = self.translations.ungettext
        tools.eq_(_(self.utf8_lemon, self.utf8_lemons, 1), self.u_limao)
        tools.eq_(_(self.utf8_limao, self.utf8_limoes, 1), self.u_lemon)
        tools.eq_(_(self.u_lemon, self.u_lemons, 1), self.u_limao)
        tools.eq_(_(self.u_limao, self.u_limoes, 1), self.u_lemon)

        tools.eq_(_(self.utf8_lemon, self.utf8_lemons, 2), self.u_limoes)
        tools.eq_(_(self.utf8_limao, self.utf8_limoes, 2), self.u_lemons)
        tools.eq_(_(self.u_lemon, self.u_lemons, 2), self.u_limoes)
        tools.eq_(_(self.u_limao, self.u_limoes, 2), self.u_lemons)

        tools.eq_(_(self.utf8_not_in_catalog, 'throwaway', 1), self.u_not_in_catalog)
        tools.eq_(_(self.u_not_in_catalog, 'throwaway', 1), self.u_not_in_catalog)


class TestNewGNURealTranslations_Latin1(TestNewGNURealTranslations_UTF8):
    def setUp(self):
        self.old_LC_ALL = os.environ.get('LC_ALL', None)
        os.environ['LC_ALL'] = 'pt_BR.iso88591'

        self.old_LANGUAGE = os.environ.pop('LANGUAGE', None)

        self.translations = i18n.get_translation_object('test', ['%s/data/locale/' % os.path.dirname(__file__)])

    def tearDown(self):
        if self.old_LC_ALL:
            os.environ['LC_ALL'] = self.old_LC_ALL
        else:
            del(os.environ['LC_ALL'])

        if self.old_LANGUAGE:
            os.environ['LANGUAGE'] = self.old_LANGUAGE

    def test_lgettext(self):
        _ = self.translations.lgettext
        tools.eq_(_(self.utf8_kitchen), self.latin1_pt_kitchen)
        tools.eq_(_(self.utf8_ja_kuratomi), self.latin1_kuratomi)
        tools.eq_(_(self.utf8_kuratomi), self.latin1_ja_kuratomi)
        # Neither of the following two tests encode to proper latin-1 because:
        # any byte is valid in latin-1 so there's no way to know that what
        # we're given in the string is really utf-8
        #
        # This is not translated to latin1_yes_in_fallback because this test
        # is without the fallback message catalog
        tools.eq_(_(self.utf8_in_fallback), self.utf8_in_fallback)
        tools.eq_(_(self.utf8_not_in_catalog), self.utf8_not_in_catalog)

        tools.eq_(_(self.u_kitchen), self.latin1_pt_kitchen)
        tools.eq_(_(self.u_ja_kuratomi), self.latin1_kuratomi)
        tools.eq_(_(self.u_kuratomi), self.latin1_ja_kuratomi)
        # This is not translated to latin1_yes_in_fallback because this test
        # is without the fallback message catalog
        tools.eq_(_(self.u_in_fallback), self.latin1_in_fallback)
        tools.eq_(_(self.u_not_in_catalog), self.latin1_not_in_catalog)

    def test_lngettext(self):
        _ = self.translations.lngettext
        tools.eq_(_(self.utf8_lemon, self.utf8_lemons, 1), self.latin1_limao)
        tools.eq_(_(self.utf8_limao, self.utf8_limoes, 1), self.latin1_lemon)
        tools.eq_(_(self.u_lemon, self.u_lemons, 1), self.latin1_limao)
        tools.eq_(_(self.u_limao, self.u_limoes, 1), self.latin1_lemon)

        tools.eq_(_(self.utf8_lemon, self.utf8_lemons, 2), self.latin1_limoes)
        tools.eq_(_(self.utf8_limao, self.utf8_limoes, 2), self.latin1_lemons)
        tools.eq_(_(self.u_lemon, self.u_lemons, 2), self.latin1_limoes)
        tools.eq_(_(self.u_limao, self.u_limoes, 2), self.latin1_lemons)

        # This unfortunately does not encode to proper latin-1 because:
        # any byte is valid in latin-1 so there's no way to know that what
        # we're given in the string is really utf-8
        tools.eq_(_(self.utf8_not_in_catalog, 'throwaway', 1), self.utf8_not_in_catalog)
        tools.eq_(_(self.u_not_in_catalog, 'throwaway', 1), self.latin1_not_in_catalog)


class TestFallbackNewGNUTranslationsNoMatch(TestDummyTranslations):
    def setUp(self):
        self.old_LC_ALL = os.environ.get('LC_ALL', None)
        os.environ['LC_ALL'] = 'pt_BR.utf8'

        self.old_LANGUAGE = os.environ.pop('LANGUAGE', None)

        self.translations = i18n.get_translation_object('test',
                ['%s/data/locale/' % os.path.dirname(__file__),
                    '%s/data/locale-old' % os.path.dirname(__file__)])

    def tearDown(self):
        if self.old_LC_ALL:
            os.environ['LC_ALL'] = self.old_LC_ALL
        else:
            del(os.environ['LC_ALL'])

        if self.old_LANGUAGE:
            os.environ['LANGUAGE'] = self.old_LANGUAGE


class TestFallbackNewGNURealTranslations_UTF8(unittest.TestCase, base_classes.UnicodeTestData):
    def setUp(self):
        self.old_LC_ALL = os.environ.get('LC_ALL', None)
        os.environ['LC_ALL'] = 'pt_BR.utf8'

        self.old_LANGUAGE = os.environ.pop('LANGUAGE', None)

        self.translations = i18n.get_translation_object('test',
                ['%s/data/locale/' % os.path.dirname(__file__),
                    '%s/data/locale-old' % os.path.dirname(__file__)])

    def tearDown(self):
        if self.old_LC_ALL:
            os.environ['LC_ALL'] = self.old_LC_ALL
        else:
            del(os.environ['LC_ALL'])

        if self.old_LANGUAGE:
            os.environ['LANGUAGE'] = self.old_LANGUAGE

    def test_gettext(self):
        _ = self.translations.gettext
        tools.eq_(_(self.utf8_kitchen), self.utf8_pt_kitchen)
        tools.eq_(_(self.utf8_ja_kuratomi), self.utf8_kuratomi)
        tools.eq_(_(self.utf8_kuratomi), self.utf8_ja_kuratomi)
        tools.eq_(_(self.utf8_in_fallback), self.utf8_yes_in_fallback)
        tools.eq_(_(self.utf8_not_in_catalog), self.utf8_not_in_catalog)

        tools.eq_(_(self.u_kitchen), self.utf8_pt_kitchen)
        tools.eq_(_(self.u_ja_kuratomi), self.utf8_kuratomi)
        tools.eq_(_(self.u_kuratomi), self.utf8_ja_kuratomi)
        tools.eq_(_(self.u_in_fallback), self.utf8_yes_in_fallback)
        tools.eq_(_(self.u_not_in_catalog), self.utf8_not_in_catalog)

    def test_ngettext(self):
        _ = self.translations.ngettext
        tools.eq_(_(self.utf8_lemon, self.utf8_lemons, 1), self.utf8_limao)
        tools.eq_(_(self.utf8_limao, self.utf8_limoes, 1), self.utf8_lemon)
        tools.eq_(_(self.u_lemon, self.u_lemons, 1), self.utf8_limao)
        tools.eq_(_(self.u_limao, self.u_limoes, 1), self.utf8_lemon)

        tools.eq_(_(self.utf8_lemon, self.utf8_lemons, 2), self.utf8_limoes)
        tools.eq_(_(self.utf8_limao, self.utf8_limoes, 2), self.utf8_lemons)
        tools.eq_(_(self.u_lemon, self.u_lemons, 2), self.utf8_limoes)
        tools.eq_(_(self.u_limao, self.u_limoes, 2), self.utf8_lemons)

        tools.eq_(_(self.utf8_not_in_catalog, 'throwaway', 1), self.utf8_not_in_catalog)
        tools.eq_(_(self.u_not_in_catalog, 'throwaway', 1), self.utf8_not_in_catalog)

    def test_lgettext(self):
        _ = self.translations.lgettext
        tools.eq_(_(self.utf8_kitchen), self.utf8_pt_kitchen)
        tools.eq_(_(self.utf8_ja_kuratomi), self.utf8_kuratomi)
        tools.eq_(_(self.utf8_kuratomi), self.utf8_ja_kuratomi)
        tools.eq_(_(self.utf8_in_fallback), self.utf8_yes_in_fallback)
        tools.eq_(_(self.utf8_not_in_catalog), self.utf8_not_in_catalog)

        tools.eq_(_(self.u_kitchen), self.utf8_pt_kitchen)
        tools.eq_(_(self.u_ja_kuratomi), self.utf8_kuratomi)
        tools.eq_(_(self.u_kuratomi), self.utf8_ja_kuratomi)
        tools.eq_(_(self.u_in_fallback), self.utf8_yes_in_fallback)
        tools.eq_(_(self.u_not_in_catalog), self.utf8_not_in_catalog)

    def test_lngettext(self):
        _ = self.translations.lngettext
        tools.eq_(_(self.utf8_lemon, self.utf8_lemons, 1), self.utf8_limao)
        tools.eq_(_(self.utf8_limao, self.utf8_limoes, 1), self.utf8_lemon)
        tools.eq_(_(self.u_lemon, self.u_lemons, 1), self.utf8_limao)
        tools.eq_(_(self.u_limao, self.u_limoes, 1), self.utf8_lemon)

        tools.eq_(_(self.utf8_lemon, self.utf8_lemons, 2), self.utf8_limoes)
        tools.eq_(_(self.utf8_limao, self.utf8_limoes, 2), self.utf8_lemons)
        tools.eq_(_(self.u_lemon, self.u_lemons, 2), self.utf8_limoes)
        tools.eq_(_(self.u_limao, self.u_limoes, 2), self.utf8_lemons)

        tools.eq_(_(self.utf8_not_in_catalog, 'throwaway', 1), self.utf8_not_in_catalog)
        tools.eq_(_(self.u_not_in_catalog, 'throwaway', 1), self.utf8_not_in_catalog)

    def test_ugettext(self):
        _ = self.translations.ugettext
        tools.eq_(_(self.utf8_kitchen), self.u_pt_kitchen)
        tools.eq_(_(self.utf8_ja_kuratomi), self.u_kuratomi)
        tools.eq_(_(self.utf8_kuratomi), self.u_ja_kuratomi)
        tools.eq_(_(self.utf8_in_fallback), self.u_yes_in_fallback)
        tools.eq_(_(self.utf8_not_in_catalog), self.u_not_in_catalog)

        tools.eq_(_(self.u_kitchen), self.u_pt_kitchen)
        tools.eq_(_(self.u_ja_kuratomi), self.u_kuratomi)
        tools.eq_(_(self.u_kuratomi), self.u_ja_kuratomi)
        tools.eq_(_(self.u_in_fallback), self.u_yes_in_fallback)
        tools.eq_(_(self.u_not_in_catalog), self.u_not_in_catalog)

    def test_ungettext(self):
        _ = self.translations.ungettext
        tools.eq_(_(self.utf8_lemon, self.utf8_lemons, 1), self.u_limao)
        tools.eq_(_(self.utf8_limao, self.utf8_limoes, 1), self.u_lemon)
        tools.eq_(_(self.u_lemon, self.u_lemons, 1), self.u_limao)
        tools.eq_(_(self.u_limao, self.u_limoes, 1), self.u_lemon)

        tools.eq_(_(self.utf8_lemon, self.utf8_lemons, 2), self.u_limoes)
        tools.eq_(_(self.utf8_limao, self.utf8_limoes, 2), self.u_lemons)
        tools.eq_(_(self.u_lemon, self.u_lemons, 2), self.u_limoes)
        tools.eq_(_(self.u_limao, self.u_limoes, 2), self.u_lemons)

        tools.eq_(_(self.utf8_not_in_catalog, 'throwaway', 1), self.u_not_in_catalog)
        tools.eq_(_(self.u_not_in_catalog, 'throwaway', 1), self.u_not_in_catalog)


class TestFallbackNewGNURealTranslations_Latin1(TestFallbackNewGNURealTranslations_UTF8):
    def setUp(self):
        self.old_LC_ALL = os.environ.get('LC_ALL', None)
        os.environ['LC_ALL'] = 'pt_BR.iso88591'

        self.old_LANGUAGE = os.environ.pop('LANGUAGE', None)

        self.translations = i18n.get_translation_object('test',
                ['%s/data/locale/' % os.path.dirname(__file__),
                    '%s/data/locale-old' % os.path.dirname(__file__)])

    def tearDown(self):
        if self.old_LC_ALL:
            os.environ['LC_ALL'] = self.old_LC_ALL
        else:
            del(os.environ['LC_ALL'])

        if self.old_LANGUAGE:
            os.environ['LANGUAGE'] = self.old_LANGUAGE

    def test_lgettext(self):
        _ = self.translations.lgettext
        tools.eq_(_(self.utf8_kitchen), self.latin1_pt_kitchen)
        tools.eq_(_(self.utf8_ja_kuratomi), self.latin1_kuratomi)
        tools.eq_(_(self.utf8_kuratomi), self.latin1_ja_kuratomi)
        tools.eq_(_(self.utf8_in_fallback), self.latin1_yes_in_fallback)
        # This unfortunately does not encode to proper latin-1 because:
        # any byte is valid in latin-1 so there's no way to know that what
        # we're given in the string is really utf-8
        tools.eq_(_(self.utf8_not_in_catalog), self.utf8_not_in_catalog)

        tools.eq_(_(self.u_kitchen), self.latin1_pt_kitchen)
        tools.eq_(_(self.u_ja_kuratomi), self.latin1_kuratomi)
        tools.eq_(_(self.u_kuratomi), self.latin1_ja_kuratomi)
        tools.eq_(_(self.u_in_fallback), self.latin1_yes_in_fallback)
        tools.eq_(_(self.u_not_in_catalog), self.latin1_not_in_catalog)

    def test_lngettext(self):
        _ = self.translations.lngettext
        tools.eq_(_(self.utf8_lemon, self.utf8_lemons, 1), self.latin1_limao)
        tools.eq_(_(self.utf8_limao, self.utf8_limoes, 1), self.latin1_lemon)
        tools.eq_(_(self.u_lemon, self.u_lemons, 1), self.latin1_limao)
        tools.eq_(_(self.u_limao, self.u_limoes, 1), self.latin1_lemon)

        tools.eq_(_(self.utf8_lemon, self.utf8_lemons, 2), self.latin1_limoes)
        tools.eq_(_(self.utf8_limao, self.utf8_limoes, 2), self.latin1_lemons)
        tools.eq_(_(self.u_lemon, self.u_lemons, 2), self.latin1_limoes)
        tools.eq_(_(self.u_limao, self.u_limoes, 2), self.latin1_lemons)

        # This unfortunately does not encode to proper latin-1 because:
        # any byte is valid in latin-1 so there's no way to know that what
        # we're given in the string is really utf-8
        tools.eq_(_(self.utf8_not_in_catalog, 'throwaway', 1), self.utf8_not_in_catalog)
        tools.eq_(_(self.u_not_in_catalog, 'throwaway', 1), self.latin1_not_in_catalog)


class TestFallback(unittest.TestCase, base_classes.UnicodeTestData):
    def setUp(self):
        self.old_LC_ALL = os.environ.get('LC_ALL', None)
        os.environ['LC_ALL'] = 'pt_BR.iso88591'

        self.old_LANGUAGE = os.environ.pop('LANGUAGE', None)

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

        if self.old_LANGUAGE:
            os.environ['LANGUAGE'] = self.old_LANGUAGE

    def test_invalid_fallback_no_raise(self):
        '''Test when we have an invalid fallback that it does not raise.'''
        tools.eq_(self.gtranslations.gettext(self.u_spanish), self.utf8_spanish)
        tools.eq_(self.gtranslations.ugettext(self.u_spanish), self.u_spanish)
        tools.eq_(self.gtranslations.lgettext(self.u_spanish), self.latin1_spanish)

        tools.eq_(self.gtranslations.ngettext(self.u_spanish, 'cde', 1), self.utf8_spanish)
        tools.eq_(self.gtranslations.ungettext(self.u_spanish, 'cde', 1), self.u_spanish)
        tools.eq_(self.gtranslations.lngettext(self.u_spanish, 'cde', 1), self.latin1_spanish)

        tools.eq_(self.dtranslations.gettext(self.u_spanish), self.utf8_spanish)
        tools.eq_(self.dtranslations.ugettext(self.u_spanish), self.u_spanish)
        tools.eq_(self.dtranslations.lgettext(self.u_spanish), self.latin1_spanish)

        tools.eq_(self.dtranslations.ngettext(self.u_spanish, 'cde', 1), self.utf8_spanish)
        tools.eq_(self.dtranslations.ungettext(self.u_spanish, 'cde', 1), self.u_spanish)
        tools.eq_(self.dtranslations.lngettext(self.u_spanish, 'cde', 1), self.latin1_spanish)


class TestDefaultLocaleDir(unittest.TestCase, base_classes.UnicodeTestData):
    def setUp(self):
        self.old_LC_ALL = os.environ.get('LC_ALL', None)
        os.environ['LC_ALL'] = 'pt_BR.utf8'

        self.old_LANGUAGE = os.environ.pop('LANGUAGE', None)

        self.old_DEFAULT_LOCALEDIRS = i18n._DEFAULT_LOCALEDIR
        i18n._DEFAULT_LOCALEDIR = '%s/data/locale/' % os.path.dirname(__file__)

        self.translations = i18n.get_translation_object('test')

    def tearDown(self):
        if self.old_LC_ALL:
            os.environ['LC_ALL'] = self.old_LC_ALL
        else:
            del(os.environ['LC_ALL'])

        if self.old_LANGUAGE:
            os.environ['LANGUAGE'] = self.old_LANGUAGE

        if self.old_DEFAULT_LOCALEDIRS:
            i18n._DEFAULT_LOCALEDIR = self.old_DEFAULT_LOCALEDIRS

    def test_gettext(self):
        _ = self.translations.gettext
        tools.eq_(_(self.utf8_kitchen), self.utf8_pt_kitchen)
        tools.eq_(_(self.utf8_kuratomi), self.utf8_ja_kuratomi)
        tools.eq_(_(self.utf8_ja_kuratomi), self.utf8_kuratomi)
        # Returns msgid because the string is in a fallback catalog which we
        # haven't setup
        tools.eq_(_(self.utf8_in_fallback), self.utf8_in_fallback)

        tools.eq_(_(self.u_kitchen), self.utf8_pt_kitchen)
        tools.eq_(_(self.u_kuratomi), self.utf8_ja_kuratomi)
        tools.eq_(_(self.u_ja_kuratomi), self.utf8_kuratomi)
        # Returns msgid because the string is in a fallback catalog which we
        # haven't setup
        tools.eq_(_(self.u_in_fallback), self.utf8_in_fallback)
