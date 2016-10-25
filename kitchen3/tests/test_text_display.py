# -*- coding: utf-8 -*-
#
import unittest
from nose import tools

from kitchen.text.exceptions import ControlCharError

from kitchen.text import display

import base_classes

class TestDisplay(base_classes.UnicodeTestData, unittest.TestCase):

    def test_internal_interval_bisearch(self):
        '''Test that we can find things in an interval table'''
        table = ((0, 3), (5, 7), (9, 10))
        tools.assert_true(display._interval_bisearch(0, table))
        tools.assert_true(display._interval_bisearch(1, table))
        tools.assert_true(display._interval_bisearch(2, table))
        tools.assert_true(display._interval_bisearch(3, table))
        tools.assert_true(display._interval_bisearch(5, table))
        tools.assert_true(display._interval_bisearch(6, table))
        tools.assert_true(display._interval_bisearch(7, table))
        tools.assert_true(display._interval_bisearch(9, table))
        tools.assert_true(display._interval_bisearch(10, table))
        tools.assert_false(display._interval_bisearch(-1, table))
        tools.assert_false(display._interval_bisearch(4, table))
        tools.assert_false(display._interval_bisearch(8, table))
        tools.assert_false(display._interval_bisearch(11, table))

    def test_internal_generate_combining_table(self):
        '''Test that the combining table we generate is equal to or a subset of what's in the current table

        If we assert it can mean one of two things:

        1. The code is broken
        2. The table we have is out of date.
        '''
        old_table = display._COMBINING
        new_table = display._generate_combining_table()
        for interval in new_table:
            if interval[0] == interval[1]:
                tools.assert_true(display._interval_bisearch(interval[0], old_table))
            else:
                for codepoint in range(interval[0], interval[1] + 1):
                    tools.assert_true(display._interval_bisearch(interval[0], old_table))

    def test_internal_ucp_width(self):
        '''Test that ucp_width returns proper width for characters'''
        for codepoint in range(0, 0xFFFFF + 1):
            if codepoint < 32 or (codepoint < 0xa0 and codepoint >= 0x7f):
                # With strict on, we should raise an error
                tools.assert_raises(ControlCharError, display._ucp_width, codepoint, 'strict')

                if codepoint in (0x08, 0x1b, 0x7f, 0x94):
                    # Backspace, delete, clear delete remove one char
                    tools.eq_(display._ucp_width(codepoint), -1)
                else:
                    # Everything else returns 0
                    tools.eq_(display._ucp_width(codepoint), 0)
            elif display._interval_bisearch(codepoint, display._COMBINING):
                # Combining character
                tools.eq_(display._ucp_width(codepoint), 0)
            elif (codepoint >= 0x1100 and
                    (codepoint <= 0x115f or                     # Hangul Jamo init. consonants
                        codepoint == 0x2329 or codepoint == 0x232a or
                        (codepoint >= 0x2e80 and codepoint <= 0xa4cf and
                            codepoint != 0x303f) or                   # CJK ... Yi
                        (codepoint >= 0xac00 and codepoint <= 0xd7a3) or # Hangul Syllables
                        (codepoint >= 0xf900 and codepoint <= 0xfaff) or # CJK Compatibility Ideographs
                        (codepoint >= 0xfe10 and codepoint <= 0xfe19) or # Vertical forms
                        (codepoint >= 0xfe30 and codepoint <= 0xfe6f) or # CJK Compatibility Forms
                        (codepoint >= 0xff00 and codepoint <= 0xff60) or # Fullwidth Forms
                        (codepoint >= 0xffe0 and codepoint <= 0xffe6) or
                        (codepoint >= 0x20000 and codepoint <= 0x2fffd) or
                        (codepoint >= 0x30000 and codepoint <= 0x3fffd))):
                tools.eq_(display._ucp_width(codepoint), 2)
            else:
                tools.eq_(display._ucp_width(codepoint), 1)

    def test_textual_width(self):
        '''Test that we find the proper number of spaces that a utf8 string will consume'''
        tools.eq_(display.textual_width(self.u_japanese), 31)
        tools.eq_(display.textual_width(self.u_spanish), 50)
        tools.eq_(display.textual_width(self.u_mixed), 23)

    def test_textual_width_chop(self):
        '''utf8_width_chop with byte strings'''
        tools.eq_(display.textual_width_chop(self.u_mixed, 1000), self.u_mixed)
        tools.eq_(display.textual_width_chop(self.u_mixed, 23), self.u_mixed)
        tools.eq_(display.textual_width_chop(self.u_mixed, 22), self.u_mixed[:-1])
        tools.eq_(display.textual_width_chop(self.u_mixed, 19), self.u_mixed[:-4])
        tools.eq_(display.textual_width_chop(self.u_mixed, 1), '')
        tools.eq_(display.textual_width_chop(self.u_mixed, 2), self.u_mixed[0])
        tools.eq_(display.textual_width_chop(self.u_mixed, 3), self.u_mixed[:2])
        tools.eq_(display.textual_width_chop(self.u_mixed, 4), self.u_mixed[:3])
        tools.eq_(display.textual_width_chop(self.u_mixed, 5), self.u_mixed[:4])
        tools.eq_(display.textual_width_chop(self.u_mixed, 6), self.u_mixed[:5])
        tools.eq_(display.textual_width_chop(self.u_mixed, 7), self.u_mixed[:5])
        tools.eq_(display.textual_width_chop(self.u_mixed, 8), self.u_mixed[:6])
        tools.eq_(display.textual_width_chop(self.u_mixed, 9), self.u_mixed[:7])
        tools.eq_(display.textual_width_chop(self.u_mixed, 10), self.u_mixed[:8])
        tools.eq_(display.textual_width_chop(self.u_mixed, 11), self.u_mixed[:9])
        tools.eq_(display.textual_width_chop(self.u_mixed, 12), self.u_mixed[:10])
        tools.eq_(display.textual_width_chop(self.u_mixed, 13), self.u_mixed[:10])
        tools.eq_(display.textual_width_chop(self.u_mixed, 14), self.u_mixed[:11])
        tools.eq_(display.textual_width_chop(self.u_mixed, 15), self.u_mixed[:12])
        tools.eq_(display.textual_width_chop(self.u_mixed, 16), self.u_mixed[:13])
        tools.eq_(display.textual_width_chop(self.u_mixed, 17), self.u_mixed[:14])
        tools.eq_(display.textual_width_chop(self.u_mixed, 18), self.u_mixed[:15])
        tools.eq_(display.textual_width_chop(self.u_mixed, 19), self.u_mixed[:15])
        tools.eq_(display.textual_width_chop(self.u_mixed, 20), self.u_mixed[:16])
        tools.eq_(display.textual_width_chop(self.u_mixed, 21), self.u_mixed[:17])

    def test_textual_width_fill(self):
        '''Pad a utf8 string'''
        tools.eq_(display.textual_width_fill(self.u_mixed, 1), self.u_mixed)
        tools.eq_(display.textual_width_fill(self.u_mixed, 25), self.u_mixed + '  ')
        tools.eq_(display.textual_width_fill(self.u_mixed, 25, left=False), '  ' + self.u_mixed)
        tools.eq_(display.textual_width_fill(self.u_mixed, 25, chop=18), self.u_mixed[:-4] + '       ')
        tools.eq_(display.textual_width_fill(self.u_mixed, 25, chop=18, prefix=self.u_spanish, suffix=self.u_spanish), self.u_spanish + self.u_mixed[:-4] + self.u_spanish + '       ')
        tools.eq_(display.textual_width_fill(self.u_mixed, 25, chop=18), self.u_mixed[:-4] + '       ')
        tools.eq_(display.textual_width_fill(self.u_mixed, 25, chop=18, prefix=self.u_spanish, suffix=self.u_spanish), self.u_spanish + self.u_mixed[:-4] + self.u_spanish + '       ')

    def test_internal_textual_width_le(self):
        test_data = ''.join([self.u_mixed, self.u_spanish])
        tw = display.textual_width(test_data)
        tools.eq_(display._textual_width_le(68, self.u_mixed, self.u_spanish), (tw <= 68))
        tools.eq_(display._textual_width_le(69, self.u_mixed, self.u_spanish), (tw <= 69))
        tools.eq_(display._textual_width_le(137, self.u_mixed, self.u_spanish), (tw <= 137))
        tools.eq_(display._textual_width_le(138, self.u_mixed, self.u_spanish), (tw <= 138))
        tools.eq_(display._textual_width_le(78, self.u_mixed, self.u_spanish), (tw <= 78))
        tools.eq_(display._textual_width_le(79, self.u_mixed, self.u_spanish), (tw <= 79))

    def test_wrap(self):
        '''Test that text wrapping works'''
        tools.eq_(display.wrap(self.u_mixed), [self.u_mixed])
        tools.eq_(display.wrap(self.u_paragraph), self.u_paragraph_out)
        tools.eq_(display.wrap(self.utf8_paragraph), self.u_paragraph_out)
        tools.eq_(display.wrap(self.u_mixed_para), self.u_mixed_para_out)
        tools.eq_(display.wrap(self.u_mixed_para, width=57,
            initial_indent='    ', subsequent_indent='----'),
            self.u_mixed_para_57_initial_subsequent_out)

    def test_fill(self):
        tools.eq_(display.fill(self.u_paragraph), '\n'.join(self.u_paragraph_out))
        tools.eq_(display.fill(self.utf8_paragraph), '\n'.join(self.u_paragraph_out))
        tools.eq_(display.fill(self.u_mixed_para), '\n'.join(self.u_mixed_para_out))
        tools.eq_(display.fill(self.u_mixed_para, width=57,
            initial_indent='    ', subsequent_indent='----'),
            '\n'.join(self.u_mixed_para_57_initial_subsequent_out))

    def test_byte_string_textual_width_fill(self):
        tools.eq_(display.byte_string_textual_width_fill(self.utf8_mixed, 1), self.utf8_mixed)
        tools.eq_(display.byte_string_textual_width_fill(self.utf8_mixed, 25), self.utf8_mixed + b'  ')
        tools.eq_(display.byte_string_textual_width_fill(self.utf8_mixed, 25, left=False), b'  ' + self.utf8_mixed)
        tools.eq_(display.byte_string_textual_width_fill(self.utf8_mixed, 25, chop=18), self.u_mixed[:-4].encode('utf8') + b'       ')
        tools.eq_(display.byte_string_textual_width_fill(self.utf8_mixed, 25, chop=18, prefix=self.utf8_spanish, suffix=self.utf8_spanish), self.utf8_spanish + self.u_mixed[:-4].encode('utf8') + self.utf8_spanish + b'       ')
        tools.eq_(display.byte_string_textual_width_fill(self.utf8_mixed, 25, chop=18), self.u_mixed[:-4].encode('utf8') + b'       ')
        tools.eq_(display.byte_string_textual_width_fill(self.utf8_mixed, 25, chop=18, prefix=self.utf8_spanish, suffix=self.utf8_spanish), self.utf8_spanish + self.u_mixed[:-4].encode('utf8') + self.utf8_spanish + b'       ')
