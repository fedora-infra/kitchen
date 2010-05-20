# -*- coding: utf-8 -*-
#

import unittest
from nose import tools
from nose.plugins.skip import SkipTest

import re

try:
    import chardet
except:
    chardet = None

from kitchen.text import converters
from kitchen.text.exceptions import XmlEncodeError

class UnicodeNoStr(object):
    def __unicode__(self):
        return u'café'

class StrNoUnicode(object):
    def __str__(self):
        return u'café'.encode('utf8')

class StrReturnsUnicode(object):
    def __str__(self):
        return u'café'

class UnicodeReturnsStr(object):
    def __unicode__(self):
        return u'café'.encode('utf8')

class UnicodeStrCrossed(object):
    def __unicode__(self):
        return u'café'.encode('utf8')

    def __str__(self):
        return u'café'

class ReprUnicode(object):
    def __repr__(self):
        return u'ReprUnicode(café)'

class TestConverters(unittest.TestCase):
    u_spanish = u'El veloz murciélago saltó sobre el perro perezoso.'
    utf8_spanish = u_spanish.encode('utf8')
    latin1_spanish = u_spanish.encode('latin1')
    u_japanese = u"速い茶色のキツネが怠惰な犬に'増"
    utf8_japanese = u_japanese.encode('utf8')
    euc_jp_japanese = u_japanese.encode('euc_jp')
    utf8_mangled_euc_jp_as_latin1 = unicode(euc_jp_japanese, 'latin1').encode('utf8')
    u_accent = u'café'
    u_accent_replace = u'caf\ufffd'
    u_accent_ignore = u'caf'
    latin1_accent = u_accent.encode('latin1')
    utf8_accent = u_accent.encode('utf8')
    u_syllabary = u'く ku'
    latin1_syllabary_replace = '? ku'
    latin1_syllabary_ignore = ' ku'
    u_entity = u'Test: <"&"> – ' + u_japanese + u'é'
    utf8_entity = u_entity.encode('utf8')
    utf8_entity_escape = 'Test: &lt;"&amp;"&gt; – 速い茶色のキツネが怠惰な犬に\'増é'
    utf8_attrib_escape = 'Test: &lt;&quot;&amp;&quot;&gt; – 速い茶色のキツネが怠惰な犬に\'増é'
    ascii_entity_escape = (u'Test: <"&"> – ' + u_japanese + u'é').encode('ascii', 'xmlcharrefreplace').replace('&', '&amp;',1).replace('<', '&lt;').replace('>', '&gt;')


    b_byte_chars = ' '.join(map(chr, range(0, 256)))
    b_byte_encoded = 'ACABIAIgAyAEIAUgBiAHIAggCSAKIAsgDCANIA4gDyAQIBEgEiATIBQgFSAWIBcgGCAZIBogGyAcIB0gHiAfICAgISAiICMgJCAlICYgJyAoICkgKiArICwgLSAuIC8gMCAxIDIgMyA0IDUgNiA3IDggOSA6IDsgPCA9ID4gPyBAIEEgQiBDIEQgRSBGIEcgSCBJIEogSyBMIE0gTiBPIFAgUSBSIFMgVCBVIFYgVyBYIFkgWiBbIFwgXSBeIF8gYCBhIGIgYyBkIGUgZiBnIGggaSBqIGsgbCBtIG4gbyBwIHEgciBzIHQgdSB2IHcgeCB5IHogeyB8IH0gfiB/IIAggSCCIIMghCCFIIYghyCIIIkgiiCLIIwgjSCOII8gkCCRIJIgkyCUIJUgliCXIJggmSCaIJsgnCCdIJ4gnyCgIKEgoiCjIKQgpSCmIKcgqCCpIKogqyCsIK0griCvILAgsSCyILMgtCC1ILYgtyC4ILkguiC7ILwgvSC+IL8gwCDBIMIgwyDEIMUgxiDHIMggySDKIMsgzCDNIM4gzyDQINEg0iDTINQg1SDWINcg2CDZINog2yDcIN0g3iDfIOAg4SDiIOMg5CDlIOYg5yDoIOkg6iDrIOwg7SDuIO8g8CDxIPIg8yD0IPUg9iD3IPgg+SD6IPsg/CD9IP4g/w=='

    repr_re = re.compile('^<[^ ]*\.([^.]+) object at .*>$')

    def test_to_unicode(self):
        '''Test to_unicode when the user gives good values'''
        tools.ok_(converters.to_unicode(self.u_japanese, encoding='latin1') == self.u_japanese)

        tools.ok_(converters.to_unicode(self.utf8_spanish) == self.u_spanish)
        tools.ok_(converters.to_unicode(self.utf8_japanese) == self.u_japanese)

        tools.ok_(converters.to_unicode(self.latin1_spanish, encoding='latin1') == self.u_spanish)
        tools.ok_(converters.to_unicode(self.euc_jp_japanese, encoding='euc_jp') == self.u_japanese)

        tools.assert_raises(TypeError, converters.to_unicode, *[5], **{'non_string': 'foo'})

    def test_to_unicode_errors(self):
        tools.ok_(converters.to_unicode(self.latin1_accent) == self.u_accent_replace)
        tools.ok_(converters.to_unicode(self.latin1_accent, errors='ignore') == self.u_accent_ignore)
        tools.assert_raises(UnicodeDecodeError, converters.to_unicode,
                *[self.latin1_accent], **{'errors': 'strict'})

    def test_to_unicode_non_string(self):
        tools.ok_(converters.to_unicode(5) == u'')
        tools.ok_(converters.to_unicode(5, non_string='passthru') == 5)
        tools.ok_(converters.to_unicode(5, non_string='simplerepr') == u'5')
        tools.ok_(converters.to_unicode(5, non_string='repr') == u'5')
        tools.assert_raises(TypeError, converters.to_unicode, *[5], **{'non_string': 'strict'})

        tools.ok_(converters.to_unicode(UnicodeNoStr(), non_string='simplerepr') == self.u_accent)
        tools.ok_(converters.to_unicode(StrNoUnicode(), non_string='simplerepr') == self.u_accent)
        tools.ok_(converters.to_unicode(StrReturnsUnicode(), non_string='simplerepr') == self.u_accent)
        tools.ok_(converters.to_unicode(UnicodeReturnsStr(), non_string='simplerepr') == self.u_accent)
        tools.ok_(converters.to_unicode(UnicodeStrCrossed(), non_string='simplerepr') == self.u_accent)

    def test_to_bytes(self):
        '''Test to_bytes when the user gives good values'''
        tools.ok_(converters.to_bytes(self.utf8_japanese, encoding='latin1') == self.utf8_japanese)

        tools.ok_(converters.to_bytes(self.u_spanish) == self.utf8_spanish)
        tools.ok_(converters.to_bytes(self.u_japanese) == self.utf8_japanese)

        tools.ok_(converters.to_bytes(self.u_spanish, encoding='latin1') == self.latin1_spanish)
        tools.ok_(converters.to_bytes(self.u_japanese, encoding='euc_jp') == self.euc_jp_japanese)

    def test_to_bytes_errors(self):
        tools.ok_(converters.to_bytes(self.u_syllabary, encoding='latin1') ==
                self.latin1_syllabary_replace)
        tools.ok_(converters.to_bytes(self.u_syllabary, encoding='latin',
            errors='ignore') == self.latin1_syllabary_ignore)
        tools.assert_raises(UnicodeEncodeError, converters.to_bytes,
            *[self.u_syllabary], **{'errors': 'strict', 'encoding': 'latin1'})

    def _check_repr_bytes(self, repr_string, obj_name):
        tools.ok_(isinstance(repr_string, str))
        match = self.repr_re.match(repr_string)
        tools.ok_(match != None)
        tools.ok_(match.groups()[0] == obj_name)

    def test_to_bytes_non_string(self):
        tools.ok_(converters.to_bytes(5) == '')
        tools.ok_(converters.to_bytes(5, non_string='passthru') == 5)
        tools.ok_(converters.to_bytes(5, non_string='simplerepr') == '5')
        tools.ok_(converters.to_bytes(5, non_string='repr') == '5')
        tools.assert_raises(TypeError, converters.to_bytes, *[5], **{'non_string': 'strict'})

        # No __str__ method so this returns repr
        string = converters.to_bytes(UnicodeNoStr(), non_string='simplerepr')
        self._check_repr_bytes(string, 'UnicodeNoStr')

        # This object's _str__ returns a utf8 encoded object
        tools.ok_(converters.to_bytes(StrNoUnicode(), non_string='simplerepr') == self.utf8_accent)

        # This object's __str__ returns unicode which to_bytes converts to utf8
        tools.ok_(converters.to_bytes(StrReturnsUnicode(), non_string='simplerepr') == self.utf8_accent)
        # Unless we explicitly ask ofr something different
        tools.ok_(converters.to_bytes(StrReturnsUnicode(),
            non_string='simplerepr', encoding='latin1') == self.latin1_accent)

        # This object has no __str__ so it returns repr
        string = converters.to_bytes(UnicodeReturnsStr(), non_string='simplerepr')
        self._check_repr_bytes(string, 'UnicodeReturnsStr')

        # This object's __str__ returns unicode which to_bytes converts to utf8
        tools.ok_(converters.to_bytes(UnicodeStrCrossed(), non_string='simplerepr') == self.utf8_accent)

        # This object's __repr__ returns unicode which to_bytes converts to utf8
        tools.ok_(converters.to_bytes(ReprUnicode(), non_string='simplerepr')
                == u'ReprUnicode(café)'.encode('utf8'))
        tools.ok_(converters.to_bytes(ReprUnicode(), non_string='repr') ==
                u'ReprUnicode(café)'.encode('utf8'))

    def test_unicode_to_xml(self):
        tools.ok_(converters.unicode_to_xml(None) == '')
        tools.assert_raises(XmlEncodeError, converters.unicode_to_xml, *['byte string'])
        tools.assert_raises(ValueError, converters.unicode_to_xml, *[u'string'], **{'control_chars': 'foo'})
        tools.assert_raises(XmlEncodeError, converters.unicode_to_xml,
                *[u'string\u0002'], **{'control_chars': 'strict'})
        tools.ok_(converters.unicode_to_xml(self.u_entity) == self.utf8_entity_escape)
        tools.ok_(converters.unicode_to_xml(self.u_entity, attrib=True) == self.utf8_attrib_escape)

    def test_xml_to_unicode(self):
        tools.ok_(converters.xml_to_unicode(self.utf8_entity_escape, 'utf8', 'replace') == self.u_entity)
        tools.ok_(converters.xml_to_unicode(self.utf8_attrib_escape, 'utf8', 'replace') == self.u_entity)

    def test_xml_to_byte_string(self):
        tools.ok_(converters.xml_to_byte_string(self.utf8_entity_escape, 'utf8', 'replace') == self.u_entity.encode('utf8'))
        tools.ok_(converters.xml_to_byte_string(self.utf8_attrib_escape, 'utf8', 'replace') == self.u_entity.encode('utf8'))

        tools.ok_(converters.xml_to_byte_string(self.utf8_attrib_escape,
            output_encoding='euc_jp', errors='replace') ==
            self.u_entity.encode('euc_jp', 'replace'))
        tools.ok_(converters.xml_to_byte_string(self.utf8_attrib_escape,
            output_encoding='latin1', errors='replace') ==
            self.u_entity.encode('latin1', 'replace'))

    def test_byte_string_to_xml(self):
        tools.assert_raises(XmlEncodeError, converters.byte_string_to_xml, *[u'test'])
        tools.ok_(converters.byte_string_to_xml(self.utf8_entity) == self.utf8_entity_escape)
        tools.ok_(converters.byte_string_to_xml(self.utf8_entity, attrib=True) == self.utf8_attrib_escape)

    def test_bytes_to_xml(self):
        tools.ok_(converters.bytes_to_xml(self.b_byte_chars) == self.b_byte_encoded)

    def test_xml_to_bytes(self):
        tools.ok_(converters.xml_to_bytes(self.b_byte_encoded) == self.b_byte_chars)

    def test_guess_encoding_to_xml(self):
        tools.ok_(converters.guess_encoding_to_xml(self.u_entity) == self.utf8_entity_escape)
        tools.ok_(converters.guess_encoding_to_xml(self.utf8_spanish) == self.utf8_spanish)
        tools.ok_(converters.guess_encoding_to_xml(self.latin1_spanish) == self.utf8_spanish)
        tools.ok_(converters.guess_encoding_to_xml(self.utf8_japanese) == self.utf8_japanese)

    def test_guess_encoding_to_xml_euc_japanese(self):
        if chardet:
            tools.ok_(converters.guess_encoding_to_xml(self.euc_jp_japanese)
                    == self.utf8_japanese)
        else:
            raise SkipTest('chardet not installed, euc_japanese won\'t be detected')

    def test_guess_encoding_to_xml_euc_japanese_mangled(self):
        if chardet:
            raise SkipTest('chardet installed, euc_japanese won\'t be mangled')
        else:
            tools.ok_(converters.guess_encoding_to_xml(self.euc_jp_japanese)
                    == self.utf8_mangled_euc_jp_as_latin1)

    def test_to_xml(self):
        tools.ok_(converters.to_xml(self.u_entity) == self.utf8_entity_escape)
        tools.ok_(converters.to_xml(self.utf8_spanish) == self.utf8_spanish)
        tools.ok_(converters.to_xml(self.latin1_spanish) == self.utf8_spanish)
        tools.ok_(converters.to_xml(self.utf8_japanese) == self.utf8_japanese)
