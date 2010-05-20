# -*- coding: utf-8 -*-
#
import unittest
from nose import tools

import __builtin__
import sets

from kitchen.pycompat24 import builtinset

class TestSetsNoOverwrite(unittest.TestCase):
    def setUp(self):
        self.set_val = None
        self.frozenset_val = None
        if not hasattr(__builtin__, 'set'):
            __builtin__.set = self.set_val
        else:
            self.set_val = __builtin__.set
        if not hasattr(__builtin__, 'frozenset'):
            __builtin__.frozenset = self.frozenset_val
        else:
            self.frozenset_val = __builtin__.frozenset

    def tearDown(self):
        if self.frozenset_val == None:
            del(__builtin__.frozenset)
        if self.set_val == None:
            del(__builtin__.set)

    def test_sets_dont_overwrite(self):
        '''Test that importing sets when there's already a set and frozenset defined does not overwrite
        '''
        builtinset.add_builtin_set()
        tools.ok_(__builtin__.set == self.set_val)
        tools.ok_(__builtin__.frozenset == self.frozenset_val)

class TestDefineSets(unittest.TestCase):
    def setUp(self):
        self.set_val = None
        self.frozenset_val = None
        if hasattr(__builtin__, 'set'):
            self.set_val = __builtin__.set
            del(__builtin__.set)
        if hasattr(__builtin__, 'frozenset'):
            self.frozenset_val = __builtin__.frozenset
            del(__builtin__.frozenset)

    def tearDown(self):
        if self.set_val:
            __builtin__.set = self.set_val
        else:
            del(__builtin__.set)
        if self.frozenset_val:
            __builtin__.frozenset = self.frozenset_val
        else:
            del(__builtin__.frozenset)

    def test_pycompat_defines_set(self):
        '''Test that importing pycompat24.sets adds set and frozenset to __builtin__
        '''
        builtinset.add_builtin_set()
        tools.ok_(__builtin__.set == sets.Set)
        tools.ok_(__builtin__.frozenset == sets.ImmutableSet)

class TestSubprocess(unittest.TestCase):
    pass

class TestBase64(unittest.TestCase):
    pass
