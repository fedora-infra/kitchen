# -*- coding: utf-8 -*-
#
import unittest
from nose import tools

from kitchen.text import utils
from kitchen.text.exceptions import ControlCharError
from kitchen.text.converters import to_unicode

class TestTextUtils(unittest.TestCase):
    u_spanish = u'El veloz murciélago saltó sobre el perro perezoso.'
    utf8_spanish = u_spanish.encode('utf8')
    latin1_spanish = u_spanish.encode('latin1')
    u_japanese = u"速い茶色のキツネが怠惰な犬に'増"
    utf8_japanese = u_japanese.encode('utf8')
    euc_jp_japanese = u_japanese.encode('euc_jp')

    u_ascii_chars = u' '.join(map(unichr, range(0, 256)))
    u_ascii_no_ctrl = u''.join([c for c in u_ascii_chars if ord(c) not in utils._control_codes])
    u_ascii_ctrl_replace = u_ascii_chars.translate(dict([(c, u'?') for c in utils._control_codes]))
    utf8_ascii_chars = u_ascii_chars.encode('utf8')

    u_entity_escape = u'Test: &lt;&quot;&amp;&quot;&gt; &ndash; ' + u_japanese.encode('ascii', 'xmlcharrefreplace') + '&#xe9;'
    u_entity = u'Test: <"&"> – ' + u_japanese + u'é'

    def test_guess_encoding_no_chardet(self):
        # Test that unicode strings are not allowed
        tools.assert_raises(TypeError, utils.guess_encoding, self.u_spanish)

        tools.ok_(utils.guess_encoding(self.utf8_spanish, disable_chardet=True) == 'utf8')
        tools.ok_(utils.guess_encoding(self.latin1_spanish, disable_chardet=True) == 'latin1')
        tools.ok_(utils.guess_encoding(self.utf8_japanese, disable_chardet=True) == 'utf8')
        tools.ok_(utils.guess_encoding(self.euc_jp_japanese, disable_chardet=True) == 'latin1')

    def test_guess_encoding_with_chardet(self):
        # We go this slightly roundabout way because multiple encodings can
        # output the same byte sequence.  What we're really interested in is
        # if we can get the original unicode string without knowing the
        # converters beforehand
        tools.ok_(to_unicode(self.utf8_spanish,
            utils.guess_encoding(self.utf8_spanish)) == self.u_spanish)
        tools.ok_(to_unicode(self.latin1_spanish,
            utils.guess_encoding(self.latin1_spanish)) == self.u_spanish)
        tools.ok_(to_unicode(self.utf8_japanese,
            utils.guess_encoding(self.utf8_japanese)) == self.u_japanese)
        tools.ok_(to_unicode(self.euc_jp_japanese,
            utils.guess_encoding(self.euc_jp_japanese)) == self.u_japanese)

    def test_str_eq(self):
        tools.ok_(utils.str_eq(self.u_japanese, self.u_japanese) == True)
        tools.ok_(utils.str_eq(self.euc_jp_japanese, self.euc_jp_japanese) == True)
        tools.ok_(utils.str_eq(self.u_japanese, self.euc_jp_japanese) == False)
        tools.ok_(utils.str_eq(self.u_japanese, self.euc_jp_japanese, encoding='euc_jp') == True)

    def test_process_control_chars(self):
        tools.assert_raises(TypeError, utils.process_control_chars, 'byte string')
        tools.assert_raises(ControlCharError, utils.process_control_chars,
                *[self.u_ascii_chars], **{'strategy':'strict'})
        tools.ok_(utils.process_control_chars(self.u_ascii_chars,
            strategy='ignore') == self.u_ascii_no_ctrl)
        tools.ok_(utils.process_control_chars(self.u_ascii_chars,
            strategy='replace') == self.u_ascii_ctrl_replace)

    def test_html_entities_unescape(self):
        tools.assert_raises(TypeError, utils.html_entities_unescape, 'byte string')
        tools.ok_(utils.html_entities_unescape(self.u_entity_escape) == self.u_entity)

    def test_byte_string_valid_xml(self):
        tools.assert_false(utils.byte_string_valid_xml(u'unicode string'))

        tools.assert_true(utils.byte_string_valid_xml(self.utf8_japanese))
        tools.assert_true(utils.byte_string_valid_xml(self.euc_jp_japanese, 'euc_jp'))

        tools.assert_false(utils.byte_string_valid_xml(self.utf8_japanese, 'euc_jp'))
        tools.assert_false(utils.byte_string_valid_xml(self.euc_jp_japanese, 'utf8'))

        tools.assert_false(utils.byte_string_valid_xml(self.utf8_ascii_chars))
