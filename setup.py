#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

from distutils.command.sdist import sdist as _sdist
import glob
import os
import sys

if sys.version_info[0] == 2:
    source_dir = 'kitchen2'
    packages = [
        'kitchen',
        'kitchen.versioning',
        'kitchen.i18n',
        'kitchen.iterutils',
        'kitchen.collections',
        'kitchen.text',
        'kitchen.pycompat24',
        'kitchen.pycompat24.base64',
        'kitchen.pycompat24.sets',
        'kitchen.pycompat25',
        'kitchen.pycompat25.collections',
        'kitchen.pycompat27',
        'kitchen.pycompat27.subprocess',
    ]
elif sys.version_info[0] == 3:
    source_dir = 'kitchen3'
    packages = [
        'kitchen',
        'kitchen.versioning',
        'kitchen.i18n',
        'kitchen.iterutils',
        'kitchen.collections',
        'kitchen.text',
        'kitchen.pycompat24',
        'kitchen.pycompat24.base64',
        'kitchen.pycompat24.sets',
        'kitchen.pycompat25',
        'kitchen.pycompat25.collections',
        'kitchen.pycompat27',
        'kitchen.pycompat27.subprocess',
    ]
else:
    raise NotImplementedError("Python version unsupported %r" % sys.version)

sys.path.append(os.path.abspath(source_dir))

# Now that we have modified sys.path, these imports will pull in either the py3
# version or the py2 version.
import kitchen.release

import releaseutils

from setuptools import setup

# Override sdist command to compile the message catalogs as well
class Sdist(_sdist, object):
    def run(self):
        releaseutils.main()
        data_files = []
        for langfile in filter(os.path.isfile, glob.glob('locale/*/*/*.mo')):
            data_files.append((os.path.dirname(langfile), [langfile]))
        if self.distribution.data_files and \
                hasattr(self.distribution.data_files, 'extend'):
            self.distribution.data_files.extend(data_files)
        else:
            self.distribution.data_files = data_files
        super(Sdist, self).run()


setup(name='kitchen',
      version=str(kitchen.release.__version__),
      description=kitchen.release.DESCRIPTION,
      long_description=kitchen.release.LONG_DESCRIPTION,
      author=kitchen.release.AUTHOR,
      author_email=kitchen.release.EMAIL,
      maintainer='Toshio Kuratomi',
      maintainer_email='toshio@fedoraproject.org',
      license=kitchen.release.LICENSE,
      url=kitchen.release.URL,
      cmdclass={'sdist': Sdist},
      keywords='Useful Small Code Snippets',
      classifiers=[
            'Development Status :: 4 - Beta',
            'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.4',
            'Programming Language :: Python :: 2.5',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Topic :: Software Development :: Internationalization',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Text Processing :: General',
          ],
      packages=packages,
      package_dir={'': source_dir},
      data_files=[],
)
