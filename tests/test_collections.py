# -*- coding: utf-8 -*-
#
import unittest
from nose import tools

from kitchen.collections.strictdict import StrictDict

def test_strict_dict_get_set():
    '''Test getting and setting items in StrictDict'''
    d = StrictDict()
    d[u'a'] = 1
    d['a'] = 2
    tools.ok_(d[u'a'] != d['a'])
    tools.ok_(len(d) == 2)

    d[u'\xf1'] = 1
    d['\xf1'] = 2
    d[u'\xf1'.encode('utf8')] = 3
    tools.ok_(d[u'\xf1'] == 1)
    tools.ok_(d['\xf1'] == 2)
    tools.ok_(d[u'\xf1'.encode('utf8')] == 3)
    tools.ok_(len(d) == 5)

class TestStrictDict(unittest.TestCase):
    def setUp(self):
        self.d = StrictDict()
        self.d[u'a'] = 1
        self.d['a'] = 2
        self.d[u'\xf1'] = 1
        self.d['\xf1'] = 2
        self.d[u'\xf1'.encode('utf8')] = 3
        self.keys = [u'a', 'a', u'\xf1', '\xf1', u'\xf1'.encode('utf8')]

    def tearDown(self):
        del(self.d)

    def _compare_lists(self, list1, list2):
        '''because we have a mixture of bytes and unicode we have to compare these lists manually and inefficiently'''
        if len(list1) != len(list2):
            return False

        list1_dupes = dict([(i, []) for i in range(1, len(list1)+1)])
        list2_dupes = dict([(i, []) for i in range(1, len(list1)+1)])


        for i in list1:
            if i not in list2:
                return False
            for n in range(1, len(list1) + 1):
                if i not in list1_dupes[n]:
                    list1_dupes[n].append(i)
                    break

        if list1_dupes[1]:
            for i in list2:
                if i not in list1:
                    return False
                for n in range(1, len(list1) +1):
                    if i not in list2_dupes[n]:
                        list2_dupes[n].append(i)
                        break

            for i in range(1, len(list1)+1):
                for n in list1_dupes:
                    if n not in list2_dupes:
                        return False

        return True

    def test_strict_dict_len(self):
        '''StrictDict len'''
        tools.ok_(len(self.d) == 5)

    def test_strict_dict_del(self):
        '''StrictDict del'''
        tools.ok_(len(self.d) == 5)
        del(self.d[u'\xf1'])
        tools.assert_raises(KeyError, self.d.__getitem__, u'\xf1')
        tools.ok_(len(self.d) == 4)

    def test_strict_dict_iter(self):
        '''StrictDict iteration'''
        keys = []
        for k in self.d:
            keys.append(k)
        tools.ok_(self._compare_lists(keys, self.keys))

        keys = []
        for k in self.d.iterkeys():
            keys.append(k)
        tools.ok_(self._compare_lists(keys, self.keys))

        keys = [k for k in self.d]
        tools.ok_(self._compare_lists(keys, self.keys))

        keys = []
        for k in self.d.keys():
            keys.append(k)
        tools.ok_(self._compare_lists(keys, self.keys))

    def test_strict_dict_contains(self):
        '''StrictDict contains function'''
        tools.assert_false('b' in self.d)
        tools.assert_false(u'b' in self.d)
        tools.ok_('\xf1' in self.d)
        tools.ok_(u'\xf1' in self.d)
        tools.ok_('a' in self.d)
        tools.ok_(u'a' in self.d)

        del(self.d[u'\xf1'])
        tools.assert_false(u'\xf1' in self.d)
        tools.ok_('\xf1' in self.d)

        del(self.d['a'])
        tools.ok_(u'a' in self.d)
        tools.assert_false('a' in self.d)
