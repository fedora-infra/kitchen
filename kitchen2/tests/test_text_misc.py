# -*- coding: utf-8 -*-
#
import unittest
from nose import tools
from nose.plugins.skip import SkipTest

try:
    import chardet
except ImportError:
    chardet = None

from kitchen.text import misc
from kitchen.text.exceptions import ControlCharError
from kitchen.text.converters import to_unicode

import base_classes

class TestTextMisc(unittest.TestCase, base_classes.UnicodeTestData):
    def test_guess_encoding_no_chardet(self):
        # Test that unicode strings are not allowed
        tools.assert_raises(TypeError, misc.guess_encoding, self.u_spanish)

        tools.ok_(misc.guess_encoding(self.utf8_spanish, disable_chardet=True) == 'utf-8')
        tools.ok_(misc.guess_encoding(self.latin1_spanish, disable_chardet=True) == 'latin-1')
        tools.ok_(misc.guess_encoding(self.utf8_japanese, disable_chardet=True) == 'utf-8')
        tools.ok_(misc.guess_encoding(self.euc_jp_japanese, disable_chardet=True) == 'latin-1')

    def test_guess_encoding_with_chardet(self):
        # We go this slightly roundabout way because multiple encodings can
        # output the same byte sequence.  What we're really interested in is
        # if we can get the original unicode string without knowing the
        # converters beforehand
        tools.ok_(to_unicode(self.utf8_spanish,
            misc.guess_encoding(self.utf8_spanish)) == self.u_spanish)
        tools.ok_(to_unicode(self.latin1_spanish,
            misc.guess_encoding(self.latin1_spanish)) == self.u_spanish)
        tools.ok_(to_unicode(self.utf8_japanese,
            misc.guess_encoding(self.utf8_japanese)) == self.u_japanese)

    def test_guess_encoding_with_chardet_installed(self):
        if chardet:
            tools.ok_(to_unicode(self.euc_jp_japanese,
                misc.guess_encoding(self.euc_jp_japanese)) == self.u_japanese)
        else:
            raise SkipTest('chardet not installed, euc_jp will not be guessed correctly')

    def test_guess_encoding_with_chardet_uninstalled(self):
        if chardet:
            raise SkipTest('chardet installed, euc_jp will not be mangled')
        else:
            tools.ok_(to_unicode(self.euc_jp_japanese,
                misc.guess_encoding(self.euc_jp_japanese)) ==
                self.u_mangled_euc_jp_as_latin1)

    def test_str_eq(self):
        # str vs str:
        tools.ok_(misc.str_eq(self.euc_jp_japanese, self.euc_jp_japanese) == True)
        tools.ok_(misc.str_eq(self.utf8_japanese, self.utf8_japanese) == True)
        tools.ok_(misc.str_eq(self.b_ascii, self.b_ascii) == True)
        tools.ok_(misc.str_eq(self.euc_jp_japanese, self.latin1_spanish) == False)
        tools.ok_(misc.str_eq(self.utf8_japanese, self.euc_jp_japanese) == False)
        tools.ok_(misc.str_eq(self.b_ascii, self.b_ascii[:-2]) == False)

        # unicode vs unicode:
        tools.ok_(misc.str_eq(self.u_japanese, self.u_japanese) == True)
        tools.ok_(misc.str_eq(self.u_ascii, self.u_ascii) == True)
        tools.ok_(misc.str_eq(self.u_japanese, self.u_spanish) == False)
        tools.ok_(misc.str_eq(self.u_ascii, self.u_ascii[:-2]) == False)

        # unicode vs str with default utf-8 conversion:
        tools.ok_(misc.str_eq(self.u_japanese, self.utf8_japanese) == True)
        tools.ok_(misc.str_eq(self.u_ascii, self.b_ascii) == True)
        tools.ok_(misc.str_eq(self.u_japanese, self.euc_jp_japanese) == False)
        tools.ok_(misc.str_eq(self.u_ascii, self.b_ascii[:-2]) == False)

        # unicode vs str with explicit encodings:
        tools.ok_(misc.str_eq(self.u_japanese, self.euc_jp_japanese, encoding='euc_jp') == True)
        tools.ok_(misc.str_eq(self.u_japanese, self.utf8_japanese, encoding='utf8') == True)
        tools.ok_(misc.str_eq(self.u_ascii, self.b_ascii, encoding='latin1') == True)
        tools.ok_(misc.str_eq(self.u_japanese, self.euc_jp_japanese, encoding='latin1') == False)
        tools.ok_(misc.str_eq(self.u_japanese, self.utf8_japanese, encoding='euc_jp') == False)
        tools.ok_(misc.str_eq(self.u_japanese, self.utf8_japanese, encoding='euc_jp') == False)
        tools.ok_(misc.str_eq(self.u_ascii, self.b_ascii[:-2], encoding='latin1') == False)

        # str vs unicode (reverse parameter order of unicode vs str)
        tools.ok_(misc.str_eq(self.utf8_japanese, self.u_japanese) == True)
        tools.ok_(misc.str_eq(self.b_ascii, self.u_ascii) == True)
        tools.ok_(misc.str_eq(self.euc_jp_japanese, self.u_japanese) == False)
        tools.ok_(misc.str_eq(self.b_ascii, self.u_ascii[:-2]) == False)

        tools.ok_(misc.str_eq(self.euc_jp_japanese, self.u_japanese, encoding='euc_jp') == True)
        tools.ok_(misc.str_eq(self.utf8_japanese, self.u_japanese, encoding='utf8') == True)
        tools.ok_(misc.str_eq(self.b_ascii, self.u_ascii, encoding='latin1') == True)
        tools.ok_(misc.str_eq(self.euc_jp_japanese, self.u_japanese, encoding='latin1') == False)
        tools.ok_(misc.str_eq(self.utf8_japanese, self.u_japanese, encoding='euc_jp') == False)
        tools.ok_(misc.str_eq(self.utf8_japanese, self.u_japanese, encoding='euc_jp') == False)
        tools.ok_(misc.str_eq(self.b_ascii, self.u_ascii[:-2], encoding='latin1') == False)


    def test_process_control_chars(self):
        tools.assert_raises(TypeError, misc.process_control_chars, 'byte string')
        tools.assert_raises(ControlCharError, misc.process_control_chars,
                *[self.u_ascii_chars], **{'strategy': 'strict'})
        tools.ok_(misc.process_control_chars(self.u_ascii_chars,
            strategy='ignore') == self.u_ascii_no_ctrl)
        tools.ok_(misc.process_control_chars(self.u_ascii_chars,
            strategy='replace') == self.u_ascii_ctrl_replace)

    def test_html_entities_unescape(self):
        tools.assert_raises(TypeError, misc.html_entities_unescape, 'byte string')
        tools.ok_(misc.html_entities_unescape(self.u_entity_escape) == self.u_entity)
        tools.ok_(misc.html_entities_unescape(u'<tag>%s</tag>'
            % self.u_entity_escape) == self.u_entity)
        tools.ok_(misc.html_entities_unescape(u'a&#1234567890;b') == u'a&#1234567890;b')
        tools.ok_(misc.html_entities_unescape(u'a&#xfffd;b') == u'a\ufffdb')
        tools.ok_(misc.html_entities_unescape(u'a&#65533;b') == u'a\ufffdb')

    def test_byte_string_valid_xml(self):
        tools.ok_(misc.byte_string_valid_xml(u'unicode string') == False)

        tools.ok_(misc.byte_string_valid_xml(self.utf8_japanese))
        tools.ok_(misc.byte_string_valid_xml(self.euc_jp_japanese, 'euc_jp'))

        tools.ok_(misc.byte_string_valid_xml(self.utf8_japanese, 'euc_jp') == False)
        tools.ok_(misc.byte_string_valid_xml(self.euc_jp_japanese, 'utf8') == False)

        tools.ok_(misc.byte_string_valid_xml(self.utf8_ascii_chars) == False)

    def test_byte_string_valid_encoding(self):
        '''Test that a byte sequence is validated'''
        tools.ok_(misc.byte_string_valid_encoding(self.utf8_japanese) == True)
        tools.ok_(misc.byte_string_valid_encoding(self.euc_jp_japanese, encoding='euc_jp') == True)

    def test_byte_string_invalid_encoding(self):
        '''Test that we return False with non-encoded chars'''
        tools.ok_(misc.byte_string_valid_encoding('\xff') == False)
        tools.ok_(misc.byte_string_valid_encoding(self.euc_jp_japanese) == False)

class TestIsStringTypes(unittest.TestCase):
    def test_isbasestring(self):
        tools.assert_true(misc.isbasestring('abc'))
        tools.assert_true(misc.isbasestring(u'abc'))
        tools.assert_false(misc.isbasestring(5))

    def test_isbytestring(self):
        tools.assert_true(misc.isbytestring('abc'))
        tools.assert_false(misc.isbytestring(u'abc'))
        tools.assert_false(misc.isbytestring(5))

    def test_isunicodestring(self):
        tools.assert_false(misc.isunicodestring('abc'))
        tools.assert_true(misc.isunicodestring(u'abc'))
        tools.assert_false(misc.isunicodestring(5))
