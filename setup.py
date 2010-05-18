# -*- coding: utf-8 -*-

from setuptools import find_packages, setup
import kitchen.release

setup(name='kitchen',
      version=kitchen.release.__version__,
      description='Kitchen contains a cornucopia of useful code',
      packages=find_packages(),
      data_files = [],
)
