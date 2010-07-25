# -*- coding: utf-8 -*-
#
import unittest
from nose import tools

from kitchen.text import display

import base_classes

class TestDisplay(base_classes.UnicodeTestData, unittest.TestCase):

    def test_textual_width(self):
        '''Test that we find the proper number of spaces that a utf8 string will consume'''
        tools.ok_(display.textual_width(self.u_japanese) == 31)
        tools.ok_(display.textual_width(self.u_spanish) == 50)
        tools.ok_(display.textual_width(self.u_mixed) == 23)

    def test_textual_width_chop(self):
        '''utf8_width_chop with byte strings'''
        tools.ok_(display.textual_width_chop(self.u_mixed, 1000) == self.u_mixed)
        tools.ok_(display.textual_width_chop(self.u_mixed, 23) == self.u_mixed)
        tools.ok_(display.textual_width_chop(self.u_mixed, 22) == self.u_mixed[:-1])
        tools.ok_(display.textual_width_chop(self.u_mixed, 19) == self.u_mixed[:-4])
        tools.ok_(display.textual_width_chop(self.u_mixed, 2) == self.u_mixed[0])
        tools.ok_(display.textual_width_chop(self.u_mixed, 1) == u'')

    def test_textual_width_fill(self):
        '''Pad a utf8 string'''
        tools.ok_(display.textual_width_fill(self.u_mixed, 1) == self.u_mixed)
        tools.ok_(display.textual_width_fill(self.u_mixed, 25) == self.u_mixed + u'  ')
        tools.ok_(display.textual_width_fill(self.u_mixed, 25, left=False) == u'  ' + self.u_mixed)
        tools.ok_(display.textual_width_fill(self.u_mixed, 25, chop=18) == self.u_mixed[:-4] + u'       ')
        tools.ok_(display.textual_width_fill(self.u_mixed, 25, chop=18, prefix=self.u_spanish, suffix=self.u_spanish) == self.u_spanish + self.u_mixed[:-4] + self.u_spanish + u'       ')
        tools.ok_(display.textual_width_fill(self.u_mixed, 25, chop=18) == self.u_mixed[:-4] + u'       ')
        tools.ok_(display.textual_width_fill(self.u_mixed, 25, chop=18, prefix=self.u_spanish, suffix=self.u_spanish) == self.u_spanish + self.u_mixed[:-4] + self.u_spanish + u'       ')
        pass

    def test_wrap(self):
        '''Test that text wrapping works'''
        tools.ok_(display.wrap(self.u_mixed) == [self.u_mixed])
        tools.ok_(display.wrap(self.paragraph) == self.paragraph_out)
        tools.ok_(display.wrap(self.u_mixed_para) == self.u_mixed_para_out)
        tools.ok_(display.wrap(self.u_mixed_para, width=57,
            initial_indent='    ', subsequent_indent='----') ==
            self.u_mixed_para_57_initial_subsequent_out)

    def test_internal_interval_bisearch(self):
        '''Test that we can find things in an interval table'''
        table = ((0, 3), (5,7), (9, 10))
        tools.ok_(display._interval_bisearch(0, table) == True)
        tools.ok_(display._interval_bisearch(1, table) == True)
        tools.ok_(display._interval_bisearch(2, table) == True)
        tools.ok_(display._interval_bisearch(3, table) == True)
        tools.ok_(display._interval_bisearch(5, table) == True)
        tools.ok_(display._interval_bisearch(6, table) == True)
        tools.ok_(display._interval_bisearch(7, table) == True)
        tools.ok_(display._interval_bisearch(9, table) == True)
        tools.ok_(display._interval_bisearch(10, table) == True)
        tools.ok_(display._interval_bisearch(-1, table) == False)
        tools.ok_(display._interval_bisearch(4, table) == False)
        tools.ok_(display._interval_bisearch(8, table) == False)
        tools.ok_(display._interval_bisearch(11, table) == False)
