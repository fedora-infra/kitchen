# -*- coding: utf-8 -*-

from nose import tools

import sys
import warnings

import importlib
from kitchen.pycompat25.collections import defaultdict

class TestPendingDeprecationModules(object):
    def __init__(self):
        kitchen_path = 'kitchen'
        collections_path = 'kitchen/collections'
        pycompat24_path = 'kitchen/pycompat24'
        pycompat25_path = 'kitchen/pycompat25'
        pycompat27_path = 'kitchen/pycompat27'

        self.module_data = (
            ('strictdict', 'kitchen.collections.strictdict', collections_path),
            ('pycompat24', 'kitchen.pycompat24', kitchen_path),
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
            importlib.find_loader(module_fqn, module_path).load_module()
            warning_raised = False
            for warning in (e.message for e in w):
                if isinstance(warning, PendingDeprecationWarning) and \
                        ('%s is deprecated' % module_name) in warning.args[0]:
                    warning_raised = True
                    break
            tools.assert_true(warning_raised, msg='%s did not raise a PendingDeprecationWarning' % module_fqn)

    def test_modules(self):
        for mod in self.module_data:
            yield self.check_modules, mod[0], mod[1], mod[2]

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
