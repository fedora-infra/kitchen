# -*- coding: utf-8 -*-
#
import unittest
from nose import tools

import warnings
from kitchen.text import encoding
#from kitchen.text import xml

class TestDeprecated(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter('error', DeprecationWarning)

    def tearDown(self):
        warnings.simplefilter('default', DeprecationWarning)

    def test_deprecated_functions(self):
        '''Test that all deprecated functions raise DeprecationWarning'''
        tools.assert_raises(DeprecationWarning, encoding.to_utf8, u'café')
        tools.assert_raises(DeprecationWarning, encoding.to_str, 5)
        #tools.assert_raises(DeprecationWarning, xml.to_xml, 'test')
