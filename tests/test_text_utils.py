# -*- coding: utf-8 -*-
#
import unittest
from nose import tools

from kitchen.text import utils
from kitchen.text.converters import to_unicode

class TestTextUtils(unittest.TestCase):
    u_spanish = u'El veloz murciélago saltó sobre el perro perezoso.'
    utf8_spanish = u_spanish.encode('utf8')
    latin1_spanish = u_spanish.encode('latin1')
    u_japanese = u"速い茶色のキツネが怠惰な犬に'増"
    utf8_japanese = u_japanese.encode('utf8')
    euc_jp_japanese = u_japanese.encode('euc_jp')

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_guess_encoding_no_chardet(self):
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
