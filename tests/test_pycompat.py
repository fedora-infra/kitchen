# -*- coding: utf-8 -*-
#
import unittest
from nose import tools

class TestUsableModules(unittest.TestCase):
    def test_subprocess(self):
        '''Test that importing subprocess as a module works
        '''
        try:
            from kitchen.pycompat24.subprocess import Popen
        except ImportError:
            tools.ok_(False, 'Unable to import pycompat24.subprocess as a module')
        try:
            from kitchen.pycompat27.subprocess import Popen
        except ImportError:
            tools.ok_(False, 'Unable to import pycompat27.subprocess as a module')

    def test_base64(self):
        '''Test that importing base64 as a module works
        '''
        try:
            from kitchen.pycompat24.base64 import b64encode
        except ImportError:
            tools.ok_(False, 'Unable to import pycompat24.base64 as a module')
