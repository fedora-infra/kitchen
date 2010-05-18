# -*- coding: utf-8 -*-
#
import unittest
from nose import tools

from kitchen.text import utf8
from kitchen.text.converters import to_bytes

class TestUTF8(unittest.TestCase):
    u_kana = u'くらとみ'
    u_accent = u'café'
    utf8_kana = u_kana.encode('utf8')
    utf8_accent = u_accent.encode('utf8')
    latin1_accent = u_accent.encode('latin1')
    u_mixed = u'く ku ら ra と to み mi'
    utf8_mixed = u_mixed.encode('utf8')
    utf8_ku = u_kana[0].encode('utf8')
    utf8_ra = u_kana[1].encode('utf8')
    utf8_to = u_kana[2].encode('utf8')
    utf8_mi = u_kana[3].encode('utf8')
    paragraph = '''ConfigObj is a simple but powerful config file reader and writer: an ini file
round tripper. Its main feature is that it is very easy to use, with a
straightforward programmer's interface and a simple syntax for config files.
It has lots of other features though:
    * Nested sections (subsections), to any level
    * List values
    * Multiple line values
    * String interpolation (substitution)
    * Integrated with a powerful validation system
          o including automatic type checking/conversion
          o repeated sections
          o and allowing default values
    * All comments in the file are preserved
    * The order of keys/sections is preserved
    * No external dependencies
    * Full Unicode support
    * A powerful unrepr mode for storing basic datatypes
'''

    paragraph_out = ['ConfigObj is a simple but powerful config file reader and writer: an',
'ini file round tripper. Its main feature is that it is very easy to',
"use, with a straightforward programmer's interface and a simple syntax",
'for config files. It has lots of other features though:',
'    * Nested sections (subsections), to any level',
'    * List values',
'    * Multiple line values',
'    * String interpolation (substitution)',
'    * Integrated with a powerful validation system',
'          o including automatic type checking/conversion',
'          o repeated sections',
'          o and allowing default values',
'    * All comments in the file are preserved',
'    * The order of keys/sections is preserved',
'    * No external dependencies',
'    * Full Unicode support',
'    * A powerful unrepr mode for storing basic datatypes']

    u_mixed_para = u'くらとみ kuratomi ' * 5
    utf8_mixed_para = u_mixed_para.encode('utf8')
    u_mixed_para_out = [u'くらとみ kuratomi くらとみ kuratomi くらとみ kuratomi くらとみ',
            u'kuratomi くらとみ kuratomi']
    u_mixed_para_57_initial_subsequent_out = [u'    くらとみ kuratomi くらとみ kuratomi くらとみ kuratomi',
        u'----くらとみ kuratomi くらとみ kuratomi']
    utf8_mixed_para_out = map(to_bytes, u_mixed_para_out)
    utf8_mixed_para_57_initial_subsequent_out = map(to_bytes, u_mixed_para_57_initial_subsequent_out)

    def test_utf8_width(self):
        '''Test that we find the proper number of spaces that a utf8 string will consume'''
        tools.ok_(utf8.utf8_width(self.utf8_kana) == 8)
        tools.ok_(utf8.utf8_width(self.utf8_accent) == 4)
        tools.ok_(utf8.utf8_width(self.utf8_mixed) == 23)

    def test_utf8_width_non_utf8(self):
        '''Test that we handle non-utf8 bytes in utf8_wdith'''
        tools.ok_(utf8.utf8_width(self.latin1_accent) == 4)

    def test_utf8_width_chop(self):
        '''utf8_width_chop with byte strings'''
        tools.ok_(utf8.utf8_width_chop(self.utf8_mixed) == (23, self.utf8_mixed))
        tools.ok_(utf8.utf8_width_chop(self.utf8_mixed, 23) == (23, self.utf8_mixed))
        tools.ok_(utf8.utf8_width_chop(self.utf8_mixed, 22) == (22, self.utf8_mixed[:-1]))
        tools.ok_(utf8.utf8_width_chop(self.utf8_mixed, 19) == (18, self.u_mixed[:-4].encode('utf8')))
        tools.ok_(utf8.utf8_width_chop(self.utf8_mixed, 2) == (2, self.u_mixed[0].encode('utf8')))
        tools.ok_(utf8.utf8_width_chop(self.utf8_mixed, 1) == (0, ''))

    def test_utf8_width_chop_unicode(self):
        '''utf8_width_chop with unicode input'''
        tools.ok_(utf8.utf8_width_chop(self.u_mixed) == (23, self.u_mixed))
        tools.ok_(utf8.utf8_width_chop(self.u_mixed, 23) == (23, self.u_mixed))
        tools.ok_(utf8.utf8_width_chop(self.u_mixed, 22) == (22, self.u_mixed[:-1]))
        tools.ok_(utf8.utf8_width_chop(self.u_mixed, 19) == (18, self.u_mixed[:-4]))
        tools.ok_(utf8.utf8_width_chop(self.u_mixed, 2) == (2, self.u_mixed[0]))
        tools.ok_(utf8.utf8_width_chop(self.u_mixed, 1) == (0, ''))

    def test_utf8_width_fill(self):
        '''Pad a utf8 string'''
        tools.ok_(utf8.utf8_width_fill(self.utf8_mixed, 1) == self.utf8_mixed)
        tools.ok_(utf8.utf8_width_fill(self.utf8_mixed, 25) == self.utf8_mixed + '  ')
        tools.ok_(utf8.utf8_width_fill(self.utf8_mixed, 25, left=False) == '  ' + self.utf8_mixed)
        tools.ok_(utf8.utf8_width_fill(self.utf8_mixed, 25, chop=18) == self.u_mixed[:-4].encode('utf8') + '       ')
        tools.ok_(utf8.utf8_width_fill(self.utf8_mixed, 25, chop=18, prefix=self.utf8_accent, suffix=self.utf8_accent) == self.utf8_accent + self.u_mixed[:-4].encode('utf8') + self.utf8_accent + '       ')
        tools.ok_(utf8.utf8_width_fill(self.utf8_mixed, 25, chop=18) == self.u_mixed[:-4].encode('utf8') + '       ')

        tools.ok_(utf8.utf8_width_fill(self.u_mixed, 25, chop=18, prefix=self.u_accent, suffix=self.utf8_accent) == self.u_accent + self.u_mixed[:-4] + self.u_accent + u'       ')
        pass

    def test_utf8_valid(self):
        '''Test that a utf8 byte sequence is validated'''
        tools.ok_(utf8.utf8_valid(self.utf8_kana) == True)
        tools.ok_(utf8.utf8_valid(self.utf8_accent) == True)

    def test_utf8_invalid(self):
        '''Test that we return False with non-utf8 chars'''
        tools.ok_(utf8.utf8_valid('\xff') == False)
        tools.ok_(utf8.utf8_valid(self.latin1_accent) == False)

    def test_utf8_text_wrap(self):
        tools.ok_(utf8.utf8_text_wrap(self.utf8_mixed) == [self.utf8_mixed])
        tools.ok_(utf8.utf8_text_wrap(self.paragraph) == self.paragraph_out)
        tools.ok_(utf8.utf8_text_wrap(self.utf8_mixed_para) == self.utf8_mixed_para_out)
        tools.ok_(utf8.utf8_text_wrap(self.utf8_mixed_para, width=57,
            initial_indent='    ', subsequent_indent='----') ==
            self.utf8_mixed_para_57_initial_subsequent_out)
