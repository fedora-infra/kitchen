#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

from distutils.command.sdist import sdist as _sdist
import glob
import os

from setuptools import find_packages, setup
import kitchen.release

import releaseutils

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
      download_url=kitchen.release.DOWNLOAD_URL,
      cmdclass={'sdist': Sdist
          },
      keywords='Useful Small Code Snippets',
      classifiers=[
            'Development Status :: 4 - Beta',
            'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2.3',
            'Programming Language :: Python :: 2.4',
            'Programming Language :: Python :: 2.5',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Topic :: Software Development :: Internationalization',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Text Processing :: General',
          ],
      packages=find_packages(),
      data_files=[],
)
