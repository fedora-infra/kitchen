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
      packages=find_packages(),
      data_files = [],
)
