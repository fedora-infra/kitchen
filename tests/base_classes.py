# -*- coding: utf-8 -*-
#
# Base class for testing unicode and utf8 functions.  This holds data that's
# useful for making tests

import re

from kitchen.text.converters import to_bytes

class UnicodeTestData(object):
    u_spanish = u'El veloz murciélago saltó sobre el perro perezoso.'
    utf8_spanish = u_spanish.encode('utf8')
    latin1_spanish = u_spanish.encode('latin1')
    u_spanish_replace = u'El veloz murci\ufffdgo salt\ufffdbre el perro perezoso.'
    u_spanish_ignore = u'El veloz murcigo saltbre el perro perezoso.'

    u_japanese = u"速い茶色のキツネが怠惰な犬に'増"
    utf8_japanese = u_japanese.encode('utf8')
    euc_jp_japanese = u_japanese.encode('euc_jp')
    utf8_mangled_euc_jp_as_latin1 = unicode(euc_jp_japanese, 'latin1').encode('utf8')

    u_mixed = u'く ku ら ra と to み mi'
    utf8_mixed = u_mixed.encode('utf8')
    utf8_ku = u_mixed[0].encode('utf8')
    utf8_ra = u_mixed[2].encode('utf8')
    utf8_to = u_mixed[4].encode('utf8')
    utf8_mi = u_mixed[6].encode('utf8')

    u_mixed_replace = u'\ufffd ku \ufffd ra \ufffd to \ufffd mi'
    u_mixed_ignore = u' ku  ra  to  mi'
    latin1_mixed_replace = '? ku ? ra ? to ? mi'
    latin1_mixed_ignore = ' ku  ra  to  mi'

    u_entity = u'Test: <"&"> – ' + u_japanese + u'é'
    utf8_entity = u_entity.encode('utf8')
    utf8_entity_escape = 'Test: &lt;"&amp;"&gt; – 速い茶色のキツネが怠惰な犬に\'増é'
    utf8_attrib_escape = 'Test: &lt;&quot;&amp;&quot;&gt; – 速い茶色のキツネが怠惰な犬に\'増é'
    ascii_entity_escape = (u'Test: <"&"> – ' + u_japanese + u'é').encode('ascii', 'xmlcharrefreplace').replace('&', '&amp;',1).replace('<', '&lt;').replace('>', '&gt;')

    b_byte_chars = ' '.join(map(chr, range(0, 256)))
    b_byte_encoded = 'ACABIAIgAyAEIAUgBiAHIAggCSAKIAsgDCANIA4gDyAQIBEgEiATIBQgFSAWIBcgGCAZIBogGyAcIB0gHiAfICAgISAiICMgJCAlICYgJyAoICkgKiArICwgLSAuIC8gMCAxIDIgMyA0IDUgNiA3IDggOSA6IDsgPCA9ID4gPyBAIEEgQiBDIEQgRSBGIEcgSCBJIEogSyBMIE0gTiBPIFAgUSBSIFMgVCBVIFYgVyBYIFkgWiBbIFwgXSBeIF8gYCBhIGIgYyBkIGUgZiBnIGggaSBqIGsgbCBtIG4gbyBwIHEgciBzIHQgdSB2IHcgeCB5IHogeyB8IH0gfiB/IIAggSCCIIMghCCFIIYghyCIIIkgiiCLIIwgjSCOII8gkCCRIJIgkyCUIJUgliCXIJggmSCaIJsgnCCdIJ4gnyCgIKEgoiCjIKQgpSCmIKcgqCCpIKogqyCsIK0griCvILAgsSCyILMgtCC1ILYgtyC4ILkguiC7ILwgvSC+IL8gwCDBIMIgwyDEIMUgxiDHIMggySDKIMsgzCDNIM4gzyDQINEg0iDTINQg1SDWINcg2CDZINog2yDcIN0g3iDfIOAg4SDiIOMg5CDlIOYg5yDoIOkg6iDrIOwg7SDuIO8g8CDxIPIg8yD0IPUg9iD3IPgg+SD6IPsg/CD9IP4g/w=='

    repr_re = re.compile('^<[^ ]*\.([^.]+) object at .*>$')

    paragraph = '''ConfigObj is a simple but powerful config file reader and writer: an ini file
round tripper. Its main feature is that it is very easy to use, with a
straightforward programmer's interface and a simple syntax for config files.
It has lots of other features though:
    * Nested sections (subsections), to any level
    * List values
    * Multiple line values
    * String interpolation (substitution)
    * Integrated with a powerful validation system
          o including automatic type checking/conversion
          o repeated sections
          o and allowing default values
    * All comments in the file are preserved
    * The order of keys/sections is preserved
    * No external dependencies
    * Full Unicode support
    * A powerful unrepr mode for storing basic datatypes
'''

    paragraph_out = ['ConfigObj is a simple but powerful config file reader and writer: an',
'ini file round tripper. Its main feature is that it is very easy to',
"use, with a straightforward programmer's interface and a simple syntax",
'for config files. It has lots of other features though:',
'    * Nested sections (subsections), to any level',
'    * List values',
'    * Multiple line values',
'    * String interpolation (substitution)',
'    * Integrated with a powerful validation system',
'          o including automatic type checking/conversion',
'          o repeated sections',
'          o and allowing default values',
'    * All comments in the file are preserved',
'    * The order of keys/sections is preserved',
'    * No external dependencies',
'    * Full Unicode support',
'    * A powerful unrepr mode for storing basic datatypes']

    u_mixed_para = u'くらとみ kuratomi ' * 5
    utf8_mixed_para = u_mixed_para.encode('utf8')
    u_mixed_para_out = [u'くらとみ kuratomi くらとみ kuratomi くらとみ kuratomi くらとみ',
            u'kuratomi くらとみ kuratomi']
    u_mixed_para_57_initial_subsequent_out = [u'    くらとみ kuratomi くらとみ kuratomi くらとみ kuratomi',
        u'----くらとみ kuratomi くらとみ kuratomi']
    utf8_mixed_para_out = map(to_bytes, u_mixed_para_out)
    utf8_mixed_para_57_initial_subsequent_out = map(to_bytes, u_mixed_para_57_initial_subsequent_out)
