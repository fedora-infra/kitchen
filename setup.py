# -*- coding: utf-8 -*-

from setuptools import find_packages, setup
import kitchen.release

setup(name='kitchen',
      version=kitchen.release.__version__,
      description=kitchen.release.DESCRIPTION,
      author=kitchen.release.AUTHOR,
      author_email=kitchen.release.EMAIL,
      license=kitchen.release.LICENSE,
      url=kitchen.release.URL,
      download_url=kitchen.release.DOWNLOAD_URL,
      keywords='Useful Small Code Snippets',
      classifiers=[
            'Development Status :: 3 - Alpha',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Programming Language :: Python :: 2.3',
            'Programming Language :: Python :: 2.4',
            'Programming Language :: Python :: 2.5',
            'Programming Language :: Python :: 2.6',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Text Processing :: General',
          ],
      packages=find_packages(),
      data_files = [],
)
