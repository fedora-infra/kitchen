# -*- coding: utf-8 -*-
#
import unittest
from nose import tools
from nose.plugins.skip import SkipTest

import __builtin__
import base64 as py_b64
import warnings

from kitchen.pycompat24 import sets
from kitchen.pycompat24.base64 import _base64 as base64

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
        sets.add_builtin_set()
        tools.ok_(__builtin__.set == self.set_val)
        tools.ok_(__builtin__.frozenset == self.frozenset_val)

class TestDefineSets(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter('ignore', DeprecationWarning)
        self.set_val = None
        self.frozenset_val = None
        if hasattr(__builtin__, 'set'):
            self.set_val = __builtin__.set
            del(__builtin__.set)
        if hasattr(__builtin__, 'frozenset'):
            self.frozenset_val = __builtin__.frozenset
            del(__builtin__.frozenset)

    def tearDown(self):
        warnings.simplefilter('default', DeprecationWarning)
        if self.set_val:
            __builtin__.set = self.set_val
        else:
            del(__builtin__.set)
        if self.frozenset_val:
            __builtin__.frozenset = self.frozenset_val
        else:
            del(__builtin__.frozenset)

    def test_pycompat_defines_set(self):
        '''Test that calling pycompat24.add_builtin_set() adds set and frozenset to __builtin__
        '''
        import sets as py_sets
        sets.add_builtin_set()
        if self.set_val:
            tools.ok_(__builtin__.set == self.set_val)
            tools.ok_(__builtin__.frozenset == self.frozenset_val)
        else:
            tools.ok_(__builtin__.set == py_sets.Set)
            tools.ok_(__builtin__.frozenset == py_sets.ImmutableSet)

class TestSubprocess(unittest.TestCase):
    pass

class TestBase64(unittest.TestCase):
    b_byte_chars = ' '.join(map(chr, range(0, 256)))
    b_byte_encoded = 'ACABIAIgAyAEIAUgBiAHIAggCSAKIAsgDCANIA4gDyAQIBEgEiATIBQgFSAWIBcgGCAZIBogGyAcIB0gHiAfICAgISAiICMgJCAlICYgJyAoICkgKiArICwgLSAuIC8gMCAxIDIgMyA0IDUgNiA3IDggOSA6IDsgPCA9ID4gPyBAIEEgQiBDIEQgRSBGIEcgSCBJIEogSyBMIE0gTiBPIFAgUSBSIFMgVCBVIFYgVyBYIFkgWiBbIFwgXSBeIF8gYCBhIGIgYyBkIGUgZiBnIGggaSBqIGsgbCBtIG4gbyBwIHEgciBzIHQgdSB2IHcgeCB5IHogeyB8IH0gfiB/IIAggSCCIIMghCCFIIYghyCIIIkgiiCLIIwgjSCOII8gkCCRIJIgkyCUIJUgliCXIJggmSCaIJsgnCCdIJ4gnyCgIKEgoiCjIKQgpSCmIKcgqCCpIKogqyCsIK0griCvILAgsSCyILMgtCC1ILYgtyC4ILkguiC7ILwgvSC+IL8gwCDBIMIgwyDEIMUgxiDHIMggySDKIMsgzCDNIM4gzyDQINEg0iDTINQg1SDWINcg2CDZINog2yDcIN0g3iDfIOAg4SDiIOMg5CDlIOYg5yDoIOkg6iDrIOwg7SDuIO8g8CDxIPIg8yD0IPUg9iD3IPgg+SD6IPsg/CD9IP4g/w=='
    b_byte_encoded_urlsafe = 'ACABIAIgAyAEIAUgBiAHIAggCSAKIAsgDCANIA4gDyAQIBEgEiATIBQgFSAWIBcgGCAZIBogGyAcIB0gHiAfICAgISAiICMgJCAlICYgJyAoICkgKiArICwgLSAuIC8gMCAxIDIgMyA0IDUgNiA3IDggOSA6IDsgPCA9ID4gPyBAIEEgQiBDIEQgRSBGIEcgSCBJIEogSyBMIE0gTiBPIFAgUSBSIFMgVCBVIFYgVyBYIFkgWiBbIFwgXSBeIF8gYCBhIGIgYyBkIGUgZiBnIGggaSBqIGsgbCBtIG4gbyBwIHEgciBzIHQgdSB2IHcgeCB5IHogeyB8IH0gfiB_IIAggSCCIIMghCCFIIYghyCIIIkgiiCLIIwgjSCOII8gkCCRIJIgkyCUIJUgliCXIJggmSCaIJsgnCCdIJ4gnyCgIKEgoiCjIKQgpSCmIKcgqCCpIKogqyCsIK0griCvILAgsSCyILMgtCC1ILYgtyC4ILkguiC7ILwgvSC-IL8gwCDBIMIgwyDEIMUgxiDHIMggySDKIMsgzCDNIM4gzyDQINEg0iDTINQg1SDWINcg2CDZINog2yDcIN0g3iDfIOAg4SDiIOMg5CDlIOYg5yDoIOkg6iDrIOwg7SDuIO8g8CDxIPIg8yD0IPUg9iD3IPgg-SD6IPsg_CD9IP4g_w=='

    def test_base64_encode(self):
        tools.ok_(base64.b64encode(self.b_byte_chars) == self.b_byte_encoded)
        tools.ok_(base64.b64encode(self.b_byte_chars, altchars='-_') == self.b_byte_encoded_urlsafe)
        tools.ok_(base64.standard_b64encode(self.b_byte_chars) == self.b_byte_encoded)
        tools.ok_(base64.urlsafe_b64encode(self.b_byte_chars) == self.b_byte_encoded_urlsafe)

        tools.ok_(base64.b64encode(self.b_byte_chars) == self.b_byte_encoded)
        tools.ok_(base64.b64encode(self.b_byte_chars, altchars='-_') == self.b_byte_encoded_urlsafe)
        tools.ok_(base64.standard_b64encode(self.b_byte_chars) == self.b_byte_encoded)
        tools.ok_(base64.urlsafe_b64encode(self.b_byte_chars) == self.b_byte_encoded_urlsafe)

    def test_base64_decode(self):
        tools.ok_(base64.b64decode(self.b_byte_encoded) == self.b_byte_chars)
        tools.ok_(base64.b64decode(self.b_byte_encoded_urlsafe, altchars='-_') == self.b_byte_chars)
        tools.ok_(base64.standard_b64decode(self.b_byte_encoded) == self.b_byte_chars)
        tools.ok_(base64.urlsafe_b64decode(self.b_byte_encoded_urlsafe) == self.b_byte_chars)

        tools.ok_(base64.b64decode(self.b_byte_encoded) == self.b_byte_chars)
        tools.ok_(base64.b64decode(self.b_byte_encoded_urlsafe, altchars='-_') == self.b_byte_chars)
        tools.ok_(base64.standard_b64decode(self.b_byte_encoded) == self.b_byte_chars)
        tools.ok_(base64.urlsafe_b64decode(self.b_byte_encoded_urlsafe) == self.b_byte_chars)

    def test_base64_stdlib_compat(self):
        if not hasattr(py_b64, 'b64encode'):
            raise SkipTest('Python-2.3 doesn\'t have b64encode to compare against')
        tools.ok_(base64.b64encode(self.b_byte_chars) == py_b64.b64encode(self.b_byte_chars))
        tools.ok_(base64.b64decode(self.b_byte_chars) == py_b64.b64decode(self.b_byte_chars))
