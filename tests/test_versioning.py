# -*- coding: utf-8 -*-
#
import unittest
from nose import tools

from kitchen.versioning import version_tuple_to_string

# Note: Using nose's generator tests for this so we can't subclass
# unittest.TestCase
class TestVersionTuple(object):
    ver_to_tuple = {u'1': ((1,),),
            u'1.0': ((1, 0),),
            u'1.0.0': ((1, 0, 0),),
            u'1.0a1': ((1, 0), ('a', 1)),
            u'1.0a1': ((1, 0), (u'a', 1)),
            u'1.0rc1': ((1, 0), ('rc', 1)),
            u'1.0rc1': ((1, 0), (u'rc', 1)),
            u'1.0rc1.2': ((1, 0), ('rc', 1, 2)),
            u'1.0rc1.2': ((1, 0), (u'rc', 1, 2)),
            u'1.0.dev345': ((1, 0), ('dev', 345)),
            u'1.0.dev345': ((1, 0), (u'dev', 345)),
            u'1.0a1.dev345': ((1, 0), ('a', 1), ('dev', 345)),
            u'1.0a1.dev345': ((1, 0), (u'a', 1), (u'dev', 345)),
            u'1.0a1.2.dev345': ((1, 0), ('a', 1, 2), ('dev', 345)),
            u'1.0a1.2.dev345': ((1, 0), (u'a', 1, 2), (u'dev', 345)),
            }

    def check_ver_tuple_to_str(self, v_tuple, v_str):
        tools.ok_(version_tuple_to_string(v_tuple) == v_str)

    def test_version_tuple_to_string(self):
        '''Test that version_tuple_to_string outputs PEP-386 compliant strings
        '''
        for v_str, v_tuple in self.ver_to_tuple.items():
            yield self.check_ver_tuple_to_str, v_tuple, v_str
