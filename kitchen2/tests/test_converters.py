# -*- coding: utf-8 -*-
#

import unittest
from nose import tools
from nose.plugins.skip import SkipTest

import sys
import StringIO
import warnings

try:
    import chardet
except:
    chardet = None

from kitchen.text import converters
from kitchen.text.exceptions import XmlEncodeError

import base_classes

class UnicodeNoStr(object):
    def __unicode__(self):
        return u'El veloz murciélago saltó sobre el perro perezoso.'

class StrNoUnicode(object):
    def __str__(self):
        return u'El veloz murciélago saltó sobre el perro perezoso.'.encode('utf8')

class StrReturnsUnicode(object):
    def __str__(self):
        return u'El veloz murciélago saltó sobre el perro perezoso.'

class UnicodeReturnsStr(object):
    def __unicode__(self):
        return u'El veloz murciélago saltó sobre el perro perezoso.'.encode('utf8')

class UnicodeStrCrossed(object):
    def __unicode__(self):
        return u'El veloz murciélago saltó sobre el perro perezoso.'.encode('utf8')

    def __str__(self):
        return u'El veloz murciélago saltó sobre el perro perezoso.'

class ReprUnicode(object):
    def __repr__(self):
        return u'ReprUnicode(El veloz murciélago saltó sobre el perro perezoso.)'

class TestConverters(unittest.TestCase, base_classes.UnicodeTestData):
    def test_to_unicode(self):
        '''Test to_unicode when the user gives good values'''
        tools.eq_(converters.to_unicode(self.u_japanese, encoding='latin1'), self.u_japanese)

        tools.eq_(converters.to_unicode(self.utf8_spanish), self.u_spanish)
        tools.eq_(converters.to_unicode(self.utf8_japanese), self.u_japanese)

        tools.eq_(converters.to_unicode(self.latin1_spanish, encoding='latin1'), self.u_spanish)
        tools.eq_(converters.to_unicode(self.euc_jp_japanese, encoding='euc_jp'), self.u_japanese)

        tools.assert_raises(TypeError, converters.to_unicode, *[5], **{'nonstring': 'foo'})

    def test_to_unicode_errors(self):
        tools.eq_(converters.to_unicode(self.latin1_spanish), self.u_mangled_spanish_latin1_as_utf8)
        tools.eq_(converters.to_unicode(self.latin1_spanish, errors='ignore'), self.u_spanish_ignore)
        tools.assert_raises(UnicodeDecodeError, converters.to_unicode,
                *[self.latin1_spanish], **{'errors': 'strict'})

    def test_to_unicode_nonstring(self):
        tools.eq_(converters.to_unicode(5), u'5')
        tools.eq_(converters.to_unicode(5, nonstring='empty'), u'')
        tools.eq_(converters.to_unicode(5, nonstring='passthru'), 5)
        tools.eq_(converters.to_unicode(5, nonstring='simplerepr'), u'5')
        tools.eq_(converters.to_unicode(5, nonstring='repr'), u'5')
        tools.assert_raises(TypeError, converters.to_unicode, *[5], **{'nonstring': 'strict'})

        obj_repr = converters.to_unicode(object, nonstring='simplerepr')
        tools.eq_(obj_repr, u"<type 'object'>")
        tools.assert_true(isinstance(obj_repr, unicode))

    def test_to_unicode_nonstring_with_objects_that_have__unicode__and__str__(self):
        '''Test that to_unicode handles objects that have  __unicode__ and  __str__ methods'''
        if sys.version_info < (3, 0):
            # None of these apply on python3 because python3 does not use __unicode__
            # and it enforces __str__ returning str
            tools.eq_(converters.to_unicode(UnicodeNoStr(), nonstring='simplerepr'), self.u_spanish)
            tools.eq_(converters.to_unicode(StrNoUnicode(), nonstring='simplerepr'), self.u_spanish)
            tools.eq_(converters.to_unicode(UnicodeReturnsStr(), nonstring='simplerepr'), self.u_spanish)

        tools.eq_(converters.to_unicode(StrReturnsUnicode(), nonstring='simplerepr'), self.u_spanish)
        tools.eq_(converters.to_unicode(UnicodeStrCrossed(), nonstring='simplerepr'), self.u_spanish)

    def test_to_bytes(self):
        '''Test to_bytes when the user gives good values'''
        tools.eq_(converters.to_bytes(self.utf8_japanese, encoding='latin1'), self.utf8_japanese)

        tools.eq_(converters.to_bytes(self.u_spanish), self.utf8_spanish)
        tools.eq_(converters.to_bytes(self.u_japanese), self.utf8_japanese)

        tools.eq_(converters.to_bytes(self.u_spanish, encoding='latin1'), self.latin1_spanish)
        tools.eq_(converters.to_bytes(self.u_japanese, encoding='euc_jp'), self.euc_jp_japanese)

    def test_to_bytes_errors(self):
        tools.eq_(converters.to_bytes(self.u_mixed, encoding='latin1'),
                self.latin1_mixed_replace)
        tools.eq_(converters.to_bytes(self.u_mixed, encoding='latin',
            errors='ignore'), self.latin1_mixed_ignore)
        tools.assert_raises(UnicodeEncodeError, converters.to_bytes,
            *[self.u_mixed], **{'errors': 'strict', 'encoding': 'latin1'})

    def _check_repr_bytes(self, repr_string, obj_name):
        tools.assert_true(isinstance(repr_string, str))
        match = self.repr_re.match(repr_string)
        tools.assert_not_equal(match, None)
        tools.eq_(match.groups()[0], obj_name)

    def test_to_bytes_nonstring(self):
        tools.eq_(converters.to_bytes(5), '5')
        tools.eq_(converters.to_bytes(5, nonstring='empty'), '')
        tools.eq_(converters.to_bytes(5, nonstring='passthru'), 5)
        tools.eq_(converters.to_bytes(5, nonstring='simplerepr'), '5')
        tools.eq_(converters.to_bytes(5, nonstring='repr'), '5')

        # Raise a TypeError if the msg is nonstring and we're set to strict
        tools.assert_raises(TypeError, converters.to_bytes, *[5], **{'nonstring': 'strict'})
        # Raise a TypeError if given an invalid nonstring arg
        tools.assert_raises(TypeError, converters.to_bytes, *[5], **{'nonstring': 'INVALID'})

        obj_repr = converters.to_bytes(object, nonstring='simplerepr')
        tools.eq_(obj_repr, "<type 'object'>")
        tools.assert_true(isinstance(obj_repr, str))

    def test_to_bytes_nonstring_with_objects_that_have__unicode__and__str__(self):
        if sys.version_info < (3, 0):
            # This object's _str__ returns a utf8 encoded object
            tools.eq_(converters.to_bytes(StrNoUnicode(), nonstring='simplerepr'), self.utf8_spanish)
        # No __str__ method so this returns repr
        string = converters.to_bytes(UnicodeNoStr(), nonstring='simplerepr')
        self._check_repr_bytes(string, 'UnicodeNoStr')

        # This object's __str__ returns unicode which to_bytes converts to utf8
        tools.eq_(converters.to_bytes(StrReturnsUnicode(), nonstring='simplerepr'), self.utf8_spanish)
        # Unless we explicitly ask for something different
        tools.eq_(converters.to_bytes(StrReturnsUnicode(),
            nonstring='simplerepr', encoding='latin1'), self.latin1_spanish)

        # This object has no __str__ so it returns repr
        string = converters.to_bytes(UnicodeReturnsStr(), nonstring='simplerepr')
        self._check_repr_bytes(string, 'UnicodeReturnsStr')

        # This object's __str__ returns unicode which to_bytes converts to utf8
        tools.eq_(converters.to_bytes(UnicodeStrCrossed(), nonstring='simplerepr'), self.utf8_spanish)

        # This object's __repr__ returns unicode which to_bytes converts to utf8
        tools.eq_(converters.to_bytes(ReprUnicode(), nonstring='simplerepr'),
                u'ReprUnicode(El veloz murciélago saltó sobre el perro perezoso.)'.encode('utf8'))
        tools.eq_(converters.to_bytes(ReprUnicode(), nonstring='repr'),
                u'ReprUnicode(El veloz murciélago saltó sobre el perro perezoso.)'.encode('utf8'))

    def test_unicode_to_xml(self):
        tools.eq_(converters.unicode_to_xml(None), '')
        tools.assert_raises(XmlEncodeError, converters.unicode_to_xml, *['byte string'])
        tools.assert_raises(ValueError, converters.unicode_to_xml, *[u'string'], **{'control_chars': 'foo'})
        tools.assert_raises(XmlEncodeError, converters.unicode_to_xml,
                *[u'string\u0002'], **{'control_chars': 'strict'})
        tools.eq_(converters.unicode_to_xml(self.u_entity), self.utf8_entity_escape)
        tools.eq_(converters.unicode_to_xml(self.u_entity, attrib=True), self.utf8_attrib_escape)
        tools.eq_(converters.unicode_to_xml(self.u_entity, encoding='ascii'), self.ascii_entity_escape)
        tools.eq_(converters.unicode_to_xml(self.u_entity, encoding='ascii', attrib=True), self.ascii_attrib_escape)

    def test_xml_to_unicode(self):
        tools.eq_(converters.xml_to_unicode(self.utf8_entity_escape, 'utf8', 'replace'), self.u_entity)
        tools.eq_(converters.xml_to_unicode(self.utf8_attrib_escape, 'utf8', 'replace'), self.u_entity)
        tools.eq_(converters.xml_to_unicode(self.ascii_entity_escape, 'ascii', 'replace'), self.u_entity)
        tools.eq_(converters.xml_to_unicode(self.ascii_attrib_escape, 'ascii', 'replace'), self.u_entity)

    def test_xml_to_byte_string(self):
        tools.eq_(converters.xml_to_byte_string(self.utf8_entity_escape, 'utf8', 'replace'), self.u_entity.encode('utf8'))
        tools.eq_(converters.xml_to_byte_string(self.utf8_attrib_escape, 'utf8', 'replace'), self.u_entity.encode('utf8'))
        tools.eq_(converters.xml_to_byte_string(self.ascii_entity_escape, 'ascii', 'replace'), self.u_entity.encode('utf8'))
        tools.eq_(converters.xml_to_byte_string(self.ascii_attrib_escape, 'ascii', 'replace'), self.u_entity.encode('utf8'))

        tools.eq_(converters.xml_to_byte_string(self.utf8_attrib_escape,
            output_encoding='euc_jp', errors='replace'),
            self.u_entity.encode('euc_jp', 'replace'))
        tools.eq_(converters.xml_to_byte_string(self.utf8_attrib_escape,
            output_encoding='latin1', errors='replace'),
            self.u_entity.encode('latin1', 'replace'))
        tools.eq_(converters.xml_to_byte_string(self.ascii_attrib_escape,
            output_encoding='euc_jp', errors='replace'),
            self.u_entity.encode('euc_jp', 'replace'))
        tools.eq_(converters.xml_to_byte_string(self.ascii_attrib_escape,
            output_encoding='latin1', errors='replace'),
            self.u_entity.encode('latin1', 'replace'))

    def test_byte_string_to_xml(self):
        tools.assert_raises(XmlEncodeError, converters.byte_string_to_xml, *[u'test'])
        tools.eq_(converters.byte_string_to_xml(self.utf8_entity), self.utf8_entity_escape)
        tools.eq_(converters.byte_string_to_xml(self.utf8_entity, attrib=True), self.utf8_attrib_escape)

    def test_bytes_to_xml(self):
        tools.eq_(converters.bytes_to_xml(self.b_byte_chars), self.b_byte_encoded)

    def test_xml_to_bytes(self):
        tools.eq_(converters.xml_to_bytes(self.b_byte_encoded), self.b_byte_chars)

    def test_guess_encoding_to_xml(self):
        tools.eq_(converters.guess_encoding_to_xml(self.u_entity), self.utf8_entity_escape)
        tools.eq_(converters.guess_encoding_to_xml(self.utf8_spanish), self.utf8_spanish)
        tools.eq_(converters.guess_encoding_to_xml(self.latin1_spanish), self.utf8_spanish)
        tools.eq_(converters.guess_encoding_to_xml(self.utf8_japanese), self.utf8_japanese)

    def test_guess_encoding_to_xml_euc_japanese(self):
        if chardet:
            tools.eq_(converters.guess_encoding_to_xml(self.euc_jp_japanese),
                    self.utf8_japanese)
        else:
            raise SkipTest('chardet not installed, euc_japanese won\'t be detected')

    def test_guess_encoding_to_xml_euc_japanese_mangled(self):
        if chardet:
            raise SkipTest('chardet installed, euc_japanese won\'t be mangled')
        else:
            tools.eq_(converters.guess_encoding_to_xml(self.euc_jp_japanese),
                    self.utf8_mangled_euc_jp_as_latin1)

class TestGetWriter(unittest.TestCase, base_classes.UnicodeTestData):
    def setUp(self):
        self.io = StringIO.StringIO()

    def test_utf8_writer(self):
        writer = converters.getwriter('utf-8')
        io = writer(self.io)
        io.write(self.u_japanese + u'\n')
        io.seek(0)
        result = io.read().strip()
        tools.eq_(result, self.utf8_japanese)

        io.seek(0)
        io.truncate(0)
        io.write(self.euc_jp_japanese + '\n')
        io.seek(0)
        result = io.read().strip()
        tools.eq_(result, self.euc_jp_japanese)

        io.seek(0)
        io.truncate(0)
        io.write(self.utf8_japanese + '\n')
        io.seek(0)
        result = io.read().strip()
        tools.eq_(result, self.utf8_japanese)

    def test_error_handlers(self):
        '''Test setting alternate error handlers'''
        writer = converters.getwriter('latin1')
        io = writer(self.io, errors='strict')
        tools.assert_raises(UnicodeEncodeError, io.write, self.u_japanese)


class TestExceptionConverters(unittest.TestCase, base_classes.UnicodeTestData):
    def setUp(self):
        self.exceptions = {}
        tests = {'u_jpn': self.u_japanese,
                'u_spanish': self.u_spanish,
                'utf8_jpn': self.utf8_japanese,
                'utf8_spanish': self.utf8_spanish,
                'euc_jpn': self.euc_jp_japanese,
                'latin1_spanish': self.latin1_spanish}
        for test in tests.iteritems():
            try:
                raise Exception(test[1])
            except Exception, self.exceptions[test[0]]:
                pass

    def test_exception_to_unicode_with_unicode(self):
        tools.eq_(converters.exception_to_unicode(self.exceptions['u_jpn']), self.u_japanese)
        tools.eq_(converters.exception_to_unicode(self.exceptions['u_spanish']), self.u_spanish)

    def test_exception_to_unicode_with_bytes(self):
        tools.eq_(converters.exception_to_unicode(self.exceptions['utf8_jpn']), self.u_japanese)
        tools.eq_(converters.exception_to_unicode(self.exceptions['utf8_spanish']), self.u_spanish)
        # Mangled latin1/utf8 conversion but no tracebacks
        tools.eq_(converters.exception_to_unicode(self.exceptions['latin1_spanish']), self.u_mangled_spanish_latin1_as_utf8)
        # Mangled euc_jp/utf8 conversion but no tracebacks
        tools.eq_(converters.exception_to_unicode(self.exceptions['euc_jpn']), self.u_mangled_euc_jp_as_utf8)

    def test_exception_to_unicode_custom(self):
        # If given custom functions, then we should not mangle
        c = [lambda e: converters.to_unicode(e.args[0], encoding='euc_jp'),
                lambda e: converters.to_unicode(e, encoding='euc_jp')]
        tools.eq_(converters.exception_to_unicode(self.exceptions['euc_jpn'],
            converters=c), self.u_japanese)
        c.extend(converters.EXCEPTION_CONVERTERS)
        tools.eq_(converters.exception_to_unicode(self.exceptions['euc_jpn'],
            converters=c), self.u_japanese)

        c = [lambda e: converters.to_unicode(e.args[0], encoding='latin1'),
                lambda e: converters.to_unicode(e, encoding='latin1')]
        tools.eq_(converters.exception_to_unicode(self.exceptions['latin1_spanish'],
            converters=c),  self.u_spanish)
        c.extend(converters.EXCEPTION_CONVERTERS)
        tools.eq_(converters.exception_to_unicode(self.exceptions['latin1_spanish'],
            converters=c),  self.u_spanish)

    def test_exception_to_bytes_with_unicode(self):
        tools.eq_(converters.exception_to_bytes(self.exceptions['u_jpn']), self.utf8_japanese)
        tools.eq_(converters.exception_to_bytes(self.exceptions['u_spanish']), self.utf8_spanish)

    def test_exception_to_bytes_with_bytes(self):
        tools.eq_(converters.exception_to_bytes(self.exceptions['utf8_jpn']), self.utf8_japanese)
        tools.eq_(converters.exception_to_bytes(self.exceptions['utf8_spanish']), self.utf8_spanish)
        tools.eq_(converters.exception_to_bytes(self.exceptions['latin1_spanish']), self.latin1_spanish)
        tools.eq_(converters.exception_to_bytes(self.exceptions['euc_jpn']), self.euc_jp_japanese)

    def test_exception_to_bytes_custom(self):
        # If given custom functions, then we should not mangle
        c = [lambda e: converters.to_bytes(e.args[0], encoding='euc_jp'),
                lambda e: converters.to_bytes(e, encoding='euc_jp')]
        tools.eq_(converters.exception_to_bytes(self.exceptions['euc_jpn'],
            converters=c), self.euc_jp_japanese)
        c.extend(converters.EXCEPTION_CONVERTERS)
        tools.eq_(converters.exception_to_bytes(self.exceptions['euc_jpn'],
            converters=c), self.euc_jp_japanese)

        c = [lambda e: converters.to_bytes(e.args[0], encoding='latin1'),
                lambda e: converters.to_bytes(e, encoding='latin1')]
        tools.eq_(converters.exception_to_bytes(self.exceptions['latin1_spanish'],
            converters=c),  self.latin1_spanish)
        c.extend(converters.EXCEPTION_CONVERTERS)
        tools.eq_(converters.exception_to_bytes(self.exceptions['latin1_spanish'],
            converters=c),  self.latin1_spanish)


class TestDeprecatedConverters(TestConverters):
    def setUp(self):
        warnings.simplefilter('ignore', DeprecationWarning)

    def tearDown(self):
        warnings.simplefilter('default', DeprecationWarning)

    def test_to_xml(self):
        tools.eq_(converters.to_xml(self.u_entity), self.utf8_entity_escape)
        tools.eq_(converters.to_xml(self.utf8_spanish), self.utf8_spanish)
        tools.eq_(converters.to_xml(self.latin1_spanish), self.utf8_spanish)
        tools.eq_(converters.to_xml(self.utf8_japanese), self.utf8_japanese)

    def test_to_utf8(self):
        tools.eq_(converters.to_utf8(self.u_japanese), self.utf8_japanese)
        tools.eq_(converters.to_utf8(self.utf8_spanish), self.utf8_spanish)

    def test_to_str(self):
        tools.eq_(converters.to_str(self.u_japanese), self.utf8_japanese)
        tools.eq_(converters.to_str(self.utf8_spanish), self.utf8_spanish)
        tools.eq_(converters.to_str(object), "<type 'object'>")

    def test_non_string(self):
        '''Test deprecated non_string parameter'''
        # unicode
        tools.assert_raises(TypeError, converters.to_unicode, *[5], **{'non_string': 'foo'})
        tools.eq_(converters.to_unicode(5, non_string='empty'), u'')
        tools.eq_(converters.to_unicode(5, non_string='passthru'), 5)
        tools.eq_(converters.to_unicode(5, non_string='simplerepr'), u'5')
        tools.eq_(converters.to_unicode(5, non_string='repr'), u'5')
        tools.assert_raises(TypeError, converters.to_unicode, *[5], **{'non_string': 'strict'})

        tools.eq_(converters.to_unicode(UnicodeNoStr(), non_string='simplerepr'), self.u_spanish)
        tools.eq_(converters.to_unicode(StrNoUnicode(), non_string='simplerepr'), self.u_spanish)
        tools.eq_(converters.to_unicode(StrReturnsUnicode(), non_string='simplerepr'), self.u_spanish)
        tools.eq_(converters.to_unicode(UnicodeReturnsStr(), non_string='simplerepr'), self.u_spanish)
        tools.eq_(converters.to_unicode(UnicodeStrCrossed(), non_string='simplerepr'), self.u_spanish)

        obj_repr = converters.to_unicode(object, non_string='simplerepr')
        tools.eq_(obj_repr, u"<type 'object'>")
        tools.assert_true(isinstance(obj_repr, unicode))

        # Bytes
        tools.eq_(converters.to_bytes(5), '5')
        tools.eq_(converters.to_bytes(5, non_string='empty'), '')
        tools.eq_(converters.to_bytes(5, non_string='passthru'), 5)
        tools.eq_(converters.to_bytes(5, non_string='simplerepr'), '5')
        tools.eq_(converters.to_bytes(5, non_string='repr'), '5')

        # Raise a TypeError if the msg is non_string and we're set to strict
        tools.assert_raises(TypeError, converters.to_bytes, *[5], **{'non_string': 'strict'})
        # Raise a TypeError if given an invalid non_string arg
        tools.assert_raises(TypeError, converters.to_bytes, *[5], **{'non_string': 'INVALID'})

        # No __str__ method so this returns repr
        string = converters.to_bytes(UnicodeNoStr(), non_string='simplerepr')
        self._check_repr_bytes(string, 'UnicodeNoStr')

        # This object's _str__ returns a utf8 encoded object
        tools.eq_(converters.to_bytes(StrNoUnicode(), non_string='simplerepr'), self.utf8_spanish)

        # This object's __str__ returns unicode which to_bytes converts to utf8
        tools.eq_(converters.to_bytes(StrReturnsUnicode(), non_string='simplerepr'), self.utf8_spanish)
        # Unless we explicitly ask for something different
        tools.eq_(converters.to_bytes(StrReturnsUnicode(),
            non_string='simplerepr', encoding='latin1'), self.latin1_spanish)

        # This object has no __str__ so it returns repr
        string = converters.to_bytes(UnicodeReturnsStr(), non_string='simplerepr')
        self._check_repr_bytes(string, 'UnicodeReturnsStr')

        # This object's __str__ returns unicode which to_bytes converts to utf8
        tools.eq_(converters.to_bytes(UnicodeStrCrossed(), non_string='simplerepr'), self.utf8_spanish)

        # This object's __repr__ returns unicode which to_bytes converts to utf8
        tools.eq_(converters.to_bytes(ReprUnicode(), non_string='simplerepr'),
                u'ReprUnicode(El veloz murciélago saltó sobre el perro perezoso.)'.encode('utf8'))
        tools.eq_(converters.to_bytes(ReprUnicode(), non_string='repr'),
                u'ReprUnicode(El veloz murciélago saltó sobre el perro perezoso.)'.encode('utf8'))

        obj_repr = converters.to_bytes(object, non_string='simplerepr')
        tools.eq_(obj_repr, "<type 'object'>")
        tools.assert_true(isinstance(obj_repr, str))
