# -*- coding: utf-8 -*-
#
import unittest
from nose import tools

import warnings
from kitchen.text import converters
from kitchen.text import utf8

class TestDeprecated(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter('error', DeprecationWarning)

    def tearDown(self):
        warnings.simplefilter('default', DeprecationWarning)

    def test_deprecated_functions(self):
        '''Test that all deprecated functions raise DeprecationWarning'''
        tools.assert_raises(DeprecationWarning, converters.to_utf8, u'café')
        tools.assert_raises(DeprecationWarning, converters.to_str, 5)
        tools.assert_raises(DeprecationWarning, converters.to_xml, 'test')

        tools.assert_raises(DeprecationWarning, utf8.utf8_valid, 'test')
        tools.assert_raises(DeprecationWarning, utf8.utf8_width, 'test')
        tools.assert_raises(DeprecationWarning, utf8.utf8_width_chop, 'test')
        tools.assert_raises(DeprecationWarning, utf8.utf8_width_fill, 'test', 'asd')
        tools.assert_raises(DeprecationWarning, utf8.utf8_text_wrap, 'test')
        tools.assert_raises(DeprecationWarning, utf8.utf8_text_fill, 'test')
        tools.assert_raises(DeprecationWarning, utf8._utf8_width_le, 'test')
