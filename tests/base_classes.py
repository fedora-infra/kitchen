# -*- coding: utf-8 -*-
#
# Base class for testing unicode and utf8 functions.  This holds data that's
# useful for making tests

import unittest

from kitchen.text.converters import to_bytes

class UnicodeTests(object):
    u_kana = u'くらとみ'
    u_accent = u'café'
    utf8_kana = u_kana.encode('utf8')
    utf8_accent = u_accent.encode('utf8')
    latin1_accent = u_accent.encode('latin1')
    u_mixed = u'く ku ら ra と to み mi'
    utf8_mixed = u_mixed.encode('utf8')
    utf8_ku = u_kana[0].encode('utf8')
    utf8_ra = u_kana[1].encode('utf8')
    utf8_to = u_kana[2].encode('utf8')
    utf8_mi = u_kana[3].encode('utf8')
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


