#!/usr/bin/python -tt
import os
import sys
import time
import urlgrabber
from hashlib import sha1

files = {
'kitchen/pycompat24/subprocess.py': 'http://svn.python.org/view/*checkout*/python/trunk/Lib/subprocess.py',
'tests/test_subprocess.py': 'http://svn.python.org/view/*checkout*/python/trunk/Lib/test/test_subprocess.py',
'tests/test_defaultdict.py': 'http://svn.python.org/view/*checkout*/python/trunk/Lib/test/test_defaultdict.py',
}

if __name__ == '__main__':
    os.chdir('sync')

    for filename in files:
        base_filename = os.path.basename(filename)
        modname = os.path.splitext(base_filename)[0]

        if not os.path.exists(modname):
            os.mkdir(modname)
            sp = open(os.path.join('..', filename), 'r')
            sp_sum = sha1(sp.read()).hexdigest()
            sp_sum_line = '%s\n' % sp_sum
            record = open('%s/record' % modname, 'w')
            record.writelines(sp_sum_line)
            record.close()

        os.chdir(modname)

        urlgrabber.urlgrab(files[filename])
        sp = open(base_filename)
        sp_sum = sha1(sp.read()).hexdigest()
        sp_sum_line = '%s\n' % sp_sum

        record = open('record', 'r')
        if sp_sum_line in record:
            os.remove(base_filename)
            sys.exit(0)

        retrieved_at = int(time.time())
        new_name = '%s-%s' % (retrieved_at, base_filename)
        os.rename(base_filename, new_name)

        print 'New %s found: %s' % (base_filename, new_name)
        record = open('record', 'a')
        record.writelines(sp_sum_line)
        record.close()
        os.chdir('..')
