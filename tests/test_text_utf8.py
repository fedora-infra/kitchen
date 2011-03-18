# -*- coding: utf-8 -*-
#
import unittest
from nose import tools

import warnings

from kitchen.text import utf8

import base_classes

class TestUTF8(base_classes.UnicodeTestData, unittest.TestCase):
    def setUp(self):
        # All of the utf8* functions are deprecated
        warnings.simplefilter('ignore', DeprecationWarning)

    def tearDown(self):
        warnings.simplefilter('default', DeprecationWarning)

    def test_utf8_width(self):
        '''Test that we find the proper number of spaces that a utf8 string will consume'''
        tools.ok_(utf8.utf8_width(self.utf8_japanese) == 31)
        tools.ok_(utf8.utf8_width(self.utf8_spanish) == 50)
        tools.ok_(utf8.utf8_width(self.utf8_mixed) == 23)

    def test_utf8_width_non_utf8(self):
        '''Test that we handle non-utf8 bytes in utf8_width without backtracing'''
        # utf8_width() treats non-utf8 byte sequences as undecodable so you
        # end up with less characters than normal.  In this string:
        # Python-2.7+ replaces problematic characters in a different manner
        # than older pythons.
        # Python >= 2.7:
        # El veloz murci�lago salt� sobre el perro perezoso.
        # Python < 2.7:
        # El veloz murci�go salt�bre el perro perezoso.
        if len(unicode(u'\xe9la'.encode('latin1'), 'utf8', 'replace')) == 1:
            # Python < 2.7
            tools.ok_(utf8.utf8_width(self.latin1_spanish) == 45)
        else:
            # Python >= 2.7
            tools.ok_(utf8.utf8_width(self.latin1_spanish) == 50)

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
        tools.ok_(utf8.utf8_width_fill(self.utf8_mixed, 25, chop=18, prefix=self.utf8_spanish, suffix=self.utf8_spanish) == self.utf8_spanish + self.u_mixed[:-4].encode('utf8') + self.utf8_spanish + '       ')
        tools.ok_(utf8.utf8_width_fill(self.utf8_mixed, 25, chop=18) == self.u_mixed[:-4].encode('utf8') + '       ')
        tools.ok_(utf8.utf8_width_fill(self.u_mixed, 25, chop=18, prefix=self.u_spanish, suffix=self.utf8_spanish) == self.u_spanish.encode('utf8') + self.u_mixed[:-4].encode('utf8') + self.u_spanish.encode('utf8') + '       ')
        pass

    def test_utf8_valid(self):
        '''Test that a utf8 byte sequence is validated'''
        warnings.simplefilter('ignore', DeprecationWarning)
        tools.ok_(utf8.utf8_valid(self.utf8_japanese) == True)
        tools.ok_(utf8.utf8_valid(self.utf8_spanish) == True)
        warnings.simplefilter('default', DeprecationWarning)

    def test_utf8_invalid(self):
        '''Test that we return False with non-utf8 chars'''
        warnings.simplefilter('ignore', DeprecationWarning)
        tools.ok_(utf8.utf8_valid('\xff') == False)
        tools.ok_(utf8.utf8_valid(self.latin1_spanish) == False)
        warnings.simplefilter('default', DeprecationWarning)

    def test_utf8_text_wrap(self):
        tools.ok_(utf8.utf8_text_wrap(self.utf8_mixed) == [self.utf8_mixed])
        tools.ok_(utf8.utf8_text_wrap(self.utf8_paragraph) == self.utf8_paragraph_out)
        tools.ok_(utf8.utf8_text_wrap(self.utf8_mixed_para) == self.utf8_mixed_para_out)
        tools.ok_(utf8.utf8_text_wrap(self.utf8_mixed_para, width=57,
            initial_indent='    ', subsequent_indent='----') ==
            self.utf8_mixed_para_57_initial_subsequent_out)
