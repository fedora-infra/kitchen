# -*- coding: utf-8 -*-
#
import unittest
from nose import tools
from nose.plugins.skip import SkipTest

import imp
import sys
import warnings
from kitchen import i18n
from kitchen.text import converters
from kitchen.text import utf8
from kitchen.pycompat25.collections import defaultdict

# Make @only_py3 decorator that will run a test on py3 but not py2
if sys.version_info >= (3, 0):
    only_py3 = tools.istest
else:
    only_py3 = SkipTest

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


class TestPendingDeprecationModules(object):
    def __init__(self):
        kitchen_path = imp.find_module('kitchen')[1]
        collections_path = imp.find_module('collections', [kitchen_path])[1]
        pycompat24_path = imp.find_module('pycompat24', [kitchen_path])[1]
        pycompat25_path = imp.find_module('pycompat25', [kitchen_path])[1]
        pycompat27_path = imp.find_module('pycompat27', [kitchen_path])[1]

        self.module_data = (
            ('strictdict', 'kitchen.collections.strictdict', collections_path),
            ('pycompat24', 'kitchen..pycompat24', kitchen_path),
            ('base64', 'kitchen.pycompat24.base64', pycompat24_path),
            ('sets', 'kitchen.pycompat24.sets', pycompat24_path),
            ('subprocess', 'kitchen.pycompat24.subprocess', pycompat24_path),
            ('pycompat25', 'kitchen.pycompat25', kitchen_path),
            ('collections', 'kitchen.pycompat25.collections', pycompat25_path),
            ('pycompat27', 'kitchen.pycompat27', kitchen_path),
            ('subprocess', 'kitchen.pycompat27.subprocess', pycompat27_path),
            )

    def setUp(self):
        for module in sys.modules.values():
            if hasattr(module, '__warningregistry__'):
                del module.__warningregistry__

    def check_modules(self, module_name, module_fqn, module_path):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            # imp.load_module will load even if it has already been loaded.
            # We need to ensure that happens in order to trigger the
            # deprecation warnings
            imp.load_module(module_fqn, *imp.find_module(module_name, [module_path]))
            warning_raised = False
            for warning in (e.message for e in w):
                if isinstance(warning, PendingDeprecationWarning) and \
                        ('%s is deprecated' % module_name) in warning.args[0]:
                    warning_raised = True
                    break
            tools.assert_true(warning_raised, msg='%s did not raise a PendingDeprecationWarning' % module_fqn)

    @only_py3
    def test_modules(self):
        for mod in self.module_data:
            yield self.check_modules, mod[0], mod[1], mod[2]

    @only_py3
    def test_defaultdict(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            defaultdict()
            warning_raised = False
            for warning in (e.message for e in w):
                if isinstance(warning, PendingDeprecationWarning) and \
                        ('defaultdict is deprecated') in warning.args[0]:
                    warning_raised = True
                    break
            tools.assert_true(warning_raised, msg='kitchen.pycompat25.collections.defaultdict did not raise a PendingDeprecationWarning')
