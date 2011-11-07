#!/usr/bin/python -tt
import os
import sys
import time
import urlgrabber
from hashlib import sha1

files = {
'kitchen/pycompat27/_subprocess.py': 'http://hg.python.org/cpython/raw-file/2.7/Lib/subprocess.py',
'tests/test_subprocess.py': 'http://hg.python.org/cpython/raw-file/2.7/Lib/test/test_subprocess.py',
'tests/test_defaultdict.py': 'http://hg.python.org/cpython/raw-file/2.7/Lib/test/test_defaultdict.py',
'kitchen/pycompat24/base64/_base64.py': 'http://hg.python.org/cpython/raw-file/2.7/Lib/base64.py',
'tests/test_base64.py': 'http://hg.python.org/cpython/raw-file/2.7/Lib/test/test_base64.py',
}
if __name__ == '__main__':
    os.chdir('sync')

    for filename in files:
        base_filename = os.path.basename(filename)
        base_upstream_filename = os.path.basename(files[filename])
        modname = os.path.splitext(base_upstream_filename)[0]

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
        sp = open(base_upstream_filename)
        sp_sum = sha1(sp.read()).hexdigest()
        sp_sum_line = '%s\n' % sp_sum

        record = open('record', 'r')
        if sp_sum_line in record:
            os.remove(base_upstream_filename)
            os.chdir('..')
            continue

        retrieved_at = int(time.time())
        new_name = '%s-%s' % (retrieved_at, base_upstream_filename)
        os.rename(base_upstream_filename, new_name)

        print 'New %s found: %s' % (base_upstream_filename, new_name)
        record = open('record', 'a')
        record.writelines(sp_sum_line)
        record.close()
        os.chdir('..')

    sys.exit(0)
