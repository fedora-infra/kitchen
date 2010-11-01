# -*- coding: utf-8 -*-
#
import unittest
from nose import tools

import os
import warnings
from kitchen.pycompat24.sets import add_builtin_set
add_builtin_set()

def logit(msg):
    log = open('/var/tmp/test.log', 'a')
    log.write('%s\n' % msg)
    log.close()

class NoAll(RuntimeError):
    pass

class FailedImport(RuntimeError):
    pass

class Test__all__(object):
    '''Test that every function in __all__ exists and that no public methods
    are missing from __all__
    '''
    known_private = set(['versioning.itertools'])
    lib_dir = os.path.join(os.path.dirname(__file__), '..', 'kitchen')

    def setUp(self):
        # Silence deprecation warnings
        warnings.simplefilter('ignore', DeprecationWarning)
    def tearDown(self):
        warnings.simplefilter('default', DeprecationWarning)

    def walk_modules(self, basedir, modpath):
        for fn in sorted(os.listdir(basedir)):
            path = os.path.join(basedir, fn)
            if os.path.isdir(path):
                pkg_init = os.path.join(path, '__init__.py')
                if os.path.exists(pkg_init):
                    yield pkg_init, modpath + fn
                    for p, m in self.walk_modules(path, modpath + fn + '.'):
                        yield p, m
                continue
            if not fn.endswith('.py') or fn == '__init__.py':
                continue
            yield path, modpath + fn[:-3]

    def check_has__all__(self, modpath):
        # This heuristic speeds up the process by removing, de facto,
        # most test modules (and avoiding the auto-executing ones).
        f = None
        try:
            f = open(modpath, 'rb')
            tools.ok_('__all__' in f.read(), '%s does not contain __all__' % modpath)
        except IOError, e:
            tools.ok_(False, '%s' % e)
        finally:
            if f:
                f.close()

    def test_has__all__(self):
        '''
        For each module, check that it has an __all__
        '''
        # Blacklisted modules and packages
        blacklist = set([ ])

        for path, modname in (m for m in self.walk_modules(self.lib_dir, '')
                if m[1] not in blacklist):
            # Check that it has an __all__
            yield self.check_has__all__, path

    def check_everything_in__all__exists(self, modname, modpath):
        names = {}
        exec 'from %s import %s' % (modpath, modname) in names
        if not hasattr(names[modname], '__all__'):
            # This should have been reported by test_has__all__
            return

        interior_names = {}
        try:
            exec 'from %s.%s import *' % (modpath, modname) in interior_names
        except Exception as e:
            # Include the module name in the exception string
            tools.ok_(False, '__all__ failure in %s: %s: %s' % (
                      modname, e.__class__.__name__, e))
        if '__builtins__' in interior_names:
            del interior_names['__builtins__']
        keys = set(interior_names)
        all = set(names[modname].__all__)
        tools.ok_(keys == all)

    def test_everything_in__all__exists(self):
        '''
        For each name in module's __all__, check that it exists
        '''
        # Blacklisted modules and packages
        blacklist = set([ ])

        for path, modname in (m for m in self.walk_modules(self.lib_dir, '')
                if m[1] not in blacklist):
            # From path, deduce the module name
            from_name = path[path.find('../kitchen') + 3:]
            if from_name.endswith('__init__.py'):
                # Remove __init__.py as well as the filename
                from_name = os.path.dirname(from_name)
            from_name = os.path.dirname(from_name)
            from_name = unicode(from_name)
            from_name = from_name.translate({ord(u'/'): u'.'})
            yield self.check_everything_in__all__exists, modname.split('.')[-1], from_name


    def check__all__is_complete(self, modname, modpath):
        names = {}
        exec 'from %s import %s' % (modpath, modname) in names
        if not hasattr(names[modname], '__all__'):
            # This should have been reported by test_has__all__
            return

        mod = names[modname]
        expected_public = [k for k in mod.__dict__ if k not in
                self.known_private and not k.startswith("_")]
        all = set(mod.__all__)
        public = set(expected_public)
        tools.ok_(all == public, 'These public names are not in %s.__all__: %s'
                % (modname, ', '.join(public.difference(all))))

    def test__all__is_complete(self):
        '''
        For each module, check that every public name is in __all__
        '''
        # Blacklisted modules and packages
        blacklist = set([ ])

        for path, modname in (m for m in self.walk_modules(self.lib_dir, '')
                if m[1] not in blacklist):
            # From path, deduce the module name
            from_name = path[path.find('../kitchen') + 3:]
            if from_name.endswith('__init__.py'):
                # Remove __init__.py as well as the filename
                from_name = os.path.dirname(from_name)
            from_name = os.path.dirname(from_name)
            from_name = unicode(from_name)
            from_name = from_name.translate({ord(u'/'): u'.'})
            yield self.check__all__is_complete, modname.split('.')[-1], from_name
