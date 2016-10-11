# -*- coding: utf-8 -*-
#
# Base class for testing unicode and utf8 functions.  This holds data that's
# useful for making tests

import re

from kitchen.text.converters import to_bytes
from kitchen.text import misc

class UnicodeTestData(object):
    u_empty_string = ''
    b_empty_string = b''
    # This should encode fine -- sanity check
    u_ascii = 'the quick brown fox jumped over the lazy dog'
    b_ascii = b'the quick brown fox jumped over the lazy dog'

    # First challenge -- what happens with latin-1 characters
    u_spanish = 'El veloz murciélago saltó sobre el perro perezoso.'
    # utf8 and latin1 both support these chars so no mangling
    utf8_spanish = u_spanish.encode('utf8')
    latin1_spanish = u_spanish.encode('latin1')

    # ASCII does not have the accented characters so it mangles
    ascii_mangled_spanish_as_ascii = u_spanish.encode('ascii', 'replace')
    # Attempting to decode using the wrong charset will mangle
    # Note: as a general principle, we do not want to have code that mangles
    # input of one charset and output of the same charset.  We want to avoid
    # things like::
    #   input latin-1, transform to unicode with utf-8, output latin-1.
    u_mangled_spanish_utf8_as_latin1 = str(utf8_spanish, encoding='latin1', errors='replace')
    u_mangled_spanish_utf8_as_ascii = str(utf8_spanish, encoding='ascii', errors='replace')
    u_mangled_spanish_latin1_as_ascii = str(latin1_spanish, encoding='ascii', errors='replace')
    u_mangled_spanish_latin1_as_utf8 = str(latin1_spanish, encoding='utf-8', errors='replace')
    ascii_twice_mangled_spanish_latin1_as_utf8_as_ascii = u_mangled_spanish_latin1_as_utf8.encode('ascii', 'replace')
    utf8_mangled_spanish_latin1_as_utf8 = u_mangled_spanish_latin1_as_utf8.encode('utf-8')
    u_spanish_ignore = str(latin1_spanish, encoding='utf8', errors='ignore')

    u_japanese = "速い茶色のキツネが怠惰な犬に'増"
    utf8_japanese = u_japanese.encode('utf8')
    euc_jp_japanese = u_japanese.encode('euc_jp')
    u_mangled_euc_jp_as_latin1 = str(euc_jp_japanese, 'latin1')
    u_mangled_euc_jp_as_utf8 = str(euc_jp_japanese, 'utf-8', 'replace')
    utf8_mangled_euc_jp_as_latin1 = u_mangled_euc_jp_as_latin1.encode('utf8')
    u_mangled_japanese_utf8_as_latin1 = str(utf8_japanese, 'latin1')
    u_mangled_japanese_utf8_as_ascii = "������������������������������������������'���"
    ascii_mangled_japanese_replace_as_latin1 = b"??????????????'?"
    latin1_mangled_japanese_replace_as_latin1 = b"??????????????'?"

    u_mixed = 'く ku ら ra と to み mi'
    utf8_mixed = u_mixed.encode('utf8')
    utf8_ku = u_mixed[0].encode('utf8')
    utf8_ra = u_mixed[2].encode('utf8')
    utf8_to = u_mixed[4].encode('utf8')
    utf8_mi = u_mixed[6].encode('utf8')

    u_mixed_replace = '\ufffd ku \ufffd ra \ufffd to \ufffd mi'
    u_mixed_ignore = ' ku  ra  to  mi'
    latin1_mixed_replace = b'? ku ? ra ? to ? mi'
    latin1_mixed_ignore = b' ku  ra  to  mi'

    u_entity = 'Test: <"&"> – ' + u_japanese + 'é'
    utf8_entity = u_entity.encode('utf8')
    u_entity_escape = 'Test: &lt;&quot;&amp;&quot;&gt; &ndash; ' + str(u_japanese.encode('ascii', 'xmlcharrefreplace'), 'ascii') + '&#xe9;'
    utf8_entity_escape = b'Test: &lt;"&amp;"&gt; ' + ('– ' + u_japanese + 'é').encode('utf8')
    utf8_attrib_escape = b'Test: &lt;&quot;&amp;&quot;&gt; ' + ('– ' + u_japanese + 'é').encode('utf8')
    ascii_entity_escape = (b'Test: <"&"> '.replace(b'&', b'&amp;', 1).replace(b'<', b'&lt;').replace(b'>', b'&gt;')) + ('– ' + u_japanese + 'é').encode('ascii', 'xmlcharrefreplace')
    ascii_attrib_escape = (b'Test: <"&"> '.replace(b'&', b'&amp;', 1).replace(b'<', b'&lt;').replace(b'>', b'&gt;').replace(b'"', b'&quot;')) + ('– ' + u_japanese + 'é').encode('ascii', 'xmlcharrefreplace')

    b_byte_chars = b' '.join((bytes((b,)) for b in range(0, 256)))
    b_byte_encoded = b'ACABIAIgAyAEIAUgBiAHIAggCSAKIAsgDCANIA4gDyAQIBEgEiATIBQgFSAWIBcgGCAZIBogGyAcIB0gHiAfICAgISAiICMgJCAlICYgJyAoICkgKiArICwgLSAuIC8gMCAxIDIgMyA0IDUgNiA3IDggOSA6IDsgPCA9ID4gPyBAIEEgQiBDIEQgRSBGIEcgSCBJIEogSyBMIE0gTiBPIFAgUSBSIFMgVCBVIFYgVyBYIFkgWiBbIFwgXSBeIF8gYCBhIGIgYyBkIGUgZiBnIGggaSBqIGsgbCBtIG4gbyBwIHEgciBzIHQgdSB2IHcgeCB5IHogeyB8IH0gfiB/IIAggSCCIIMghCCFIIYghyCIIIkgiiCLIIwgjSCOII8gkCCRIJIgkyCUIJUgliCXIJggmSCaIJsgnCCdIJ4gnyCgIKEgoiCjIKQgpSCmIKcgqCCpIKogqyCsIK0griCvILAgsSCyILMgtCC1ILYgtyC4ILkguiC7ILwgvSC+IL8gwCDBIMIgwyDEIMUgxiDHIMggySDKIMsgzCDNIM4gzyDQINEg0iDTINQg1SDWINcg2CDZINog2yDcIN0g3iDfIOAg4SDiIOMg5CDlIOYg5yDoIOkg6iDrIOwg7SDuIO8g8CDxIPIg8yD0IPUg9iD3IPgg+SD6IPsg/CD9IP4g/w=='

    repr_re = re.compile(b'^<[^ ]*\.([^.]+) object at .*>$')

    u_paragraph = '''ConfigObj is a simple but powerful config file reader and writer: an ini file
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
    utf8_paragraph = u_paragraph.encode('utf-8', 'replace')
    u_paragraph_out = ['ConfigObj is a simple but powerful config file reader and writer: an',
'ini file round tripper. Its main feature is that it is very easy to',
"use, with a straightforward programmer's interface and a simple syntax",
'for config files. It has lots of other features though:',
'',
'',
'',
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

    utf8_paragraph_out = [line.encode('utf-8', 'replace') for line in u_paragraph_out]

    u_mixed_para = 'くらとみ kuratomi ' * 5
    utf8_mixed_para = u_mixed_para.encode('utf8')
    u_mixed_para_out = ['くらとみ kuratomi くらとみ kuratomi くらとみ kuratomi くらとみ',
            'kuratomi くらとみ kuratomi']
    u_mixed_para_57_initial_subsequent_out = ['    くらとみ kuratomi くらとみ kuratomi くらとみ kuratomi',
        '----くらとみ kuratomi くらとみ kuratomi']
    utf8_mixed_para_out = list(map(to_bytes, u_mixed_para_out))
    utf8_mixed_para_57_initial_subsequent_out = list(map(to_bytes, u_mixed_para_57_initial_subsequent_out))

    u_ascii_chars = ' '.join(map(chr, list(range(0, 256))))
    u_ascii_no_ctrl = ''.join([c for c in u_ascii_chars if ord(c) not in misc._CONTROL_CODES])
    u_ascii_ctrl_replace = u_ascii_chars.translate(dict([(c, '?') for c in misc._CONTROL_CODES]))
    utf8_ascii_chars = u_ascii_chars.encode('utf8')

    # These are present in the test catalog as msgids or values
    u_lemon = '1 lemon'
    utf8_lemon = u_lemon.encode('utf-8')
    latin1_lemon = u_lemon.encode('latin-1')

    u_lemons = '4 lemons'
    utf8_lemons = u_lemons.encode('utf-8')
    latin1_lemons = u_lemons.encode('latin-1')

    u_limao = '一 limão'
    utf8_limao = u_limao.encode('utf-8')
    latin1_limao = u_limao.encode('latin-1', 'replace')

    u_limoes = '四 limões'
    utf8_limoes = u_limoes.encode('utf-8')
    latin1_limoes = u_limoes.encode('latin-1', 'replace')

    u_not_in_catalog = 'café not matched in catalogs'
    utf8_not_in_catalog = u_not_in_catalog.encode('utf-8')
    latin1_not_in_catalog = u_not_in_catalog.encode('latin-1')

    u_kitchen = 'kitchen sink'
    utf8_kitchen = u_kitchen.encode('utf-8')
    latin1_kitchen = u_kitchen.encode('latin-1')

    u_pt_kitchen = 'pia da cozinha'
    utf8_pt_kitchen = u_pt_kitchen.encode('utf-8')
    latin1_pt_kitchen = u_pt_kitchen.encode('latin-1')

    u_kuratomi = 'Kuratomi'
    utf8_kuratomi = u_kuratomi.encode('utf-8')
    latin1_kuratomi = u_kuratomi.encode('latin-1')

    u_ja_kuratomi = 'くらとみ'
    utf8_ja_kuratomi = u_ja_kuratomi.encode('utf-8')
    latin1_ja_kuratomi = u_ja_kuratomi.encode('latin-1', 'replace')

    u_in_fallback = 'Only café in fallback'
    utf8_in_fallback = u_in_fallback.encode('utf-8')
    latin1_in_fallback = u_in_fallback.encode('latin-1')

    u_yes_in_fallback = 'Yes, only café in fallback'
    utf8_yes_in_fallback = u_yes_in_fallback.encode('utf-8')
    latin1_yes_in_fallback = u_yes_in_fallback.encode('latin-1')
