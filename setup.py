# -*- coding: utf-8 -*-

from distutils.core import setup
from glob import glob
import kitchen

setup(name='kitchen',
      version=kitchen.release.__version__,
      description='Kitchen contains a cornucopia of useful code',
      packages=['kitchen'],
      data_files = [],

)
