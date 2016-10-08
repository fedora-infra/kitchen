# -*- coding: utf-8 -*-
#
import unittest
from nose import tools

import sys
import warnings
from kitchen import i18n
from kitchen.text import converters
from kitchen.text import utf8

class TestDeprecated(unittest.TestCase):
    def setUp(self):
        for module in sys.modules.values():
            if hasattr(module, '__warningregistry__'):
                del module.__warningregistry__
        warnings.simplefilter('error', DeprecationWarning)

    def tearDown(self):
        warnings.simplefilter('ignore', DeprecationWarning)

    def test_deprecated_functions(self):
        '''Test that all deprecated functions raise DeprecationWarning'''
        tools.assert_raises(DeprecationWarning, converters.to_utf8, 'café')
        tools.assert_raises(DeprecationWarning, converters.to_str, 5)
        tools.assert_raises(DeprecationWarning, converters.to_xml, 'test')

        tools.assert_raises(DeprecationWarning, utf8.utf8_valid, 'test')
        tools.assert_raises(DeprecationWarning, utf8.utf8_width, 'test')
        tools.assert_raises(DeprecationWarning, utf8.utf8_width_chop, 'test')
        tools.assert_raises(DeprecationWarning, utf8.utf8_width_fill, 'test', 'asd')
        tools.assert_raises(DeprecationWarning, utf8.utf8_text_wrap, 'test')
        tools.assert_raises(DeprecationWarning, utf8.utf8_text_fill, 'test')
        tools.assert_raises(DeprecationWarning, utf8._utf8_width_le, 'test')

    def test_deprecated_parameters(self):
        tools.assert_raises(DeprecationWarning, converters.to_unicode, *[5],
                **{'non_string': 'simplerepr'})
        tools.assert_raises(DeprecationWarning, converters.to_unicode, *[5],
                **{'nonstring': 'simplerepr', 'non_string': 'simplerepr'})

        tools.assert_raises(DeprecationWarning, converters.to_bytes, *[5],
                **{'non_string': 'simplerepr'})
        tools.assert_raises(DeprecationWarning, converters.to_bytes, *[5],
                **{'nonstring': 'simplerepr', 'non_string': 'simplerepr'})


class TestPendingDeprecationParameters(unittest.TestCase):
    def setUp(self):
        for module in sys.modules.values():
            if hasattr(module, '__warningregistry__'):
                del module.__warningregistry__
        warnings.simplefilter('error', PendingDeprecationWarning)

    def tearDown(self):
        warnings.simplefilter('ignore', PendingDeprecationWarning)

    def test_parameters(self):
        # test that we warn when using the python2_api parameters
        tools.assert_raises(PendingDeprecationWarning,
                i18n.get_translation_object, 'test', **{'python2_api': True})
        tools.assert_raises(PendingDeprecationWarning,
                i18n.DummyTranslations, **{'python2_api': True})
