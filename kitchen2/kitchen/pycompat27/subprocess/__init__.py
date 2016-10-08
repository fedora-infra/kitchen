# -*- coding: utf-8 -*-
#
# Copyright (c) 2011 Red Hat, Inc
#
# This file is part of kitchen
#
# kitchen is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# kitchen is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for
# more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with kitchen; if not, see <http://www.gnu.org/licenses/>
#
# Authors:
#   Toshio Kuratomi <toshio@fedoraproject.org>

'''
Implement the modern subprocess interface

Python-2.5 and python-2.7 introduce new API features to subprocess.  This is
a backport of that module for use on earlier python versions.

.. seealso::
    :mod:`subprocess`
        for information about using the functions provided here.
'''
import sys

# :W0401,W0611,W0614: We're importing compatibility to the python-2.7 version
#   of subprocess.
#pylint:disable-msg=W0401,W0611,W0614
if sys.version_info >= (2, 7):
    from subprocess import *
    from subprocess import MAXFD, list2cmdline, mswindows
    from subprocess import __all__
else:
    from kitchen.pycompat27.subprocess._subprocess import *
    from kitchen.pycompat27.subprocess._subprocess import MAXFD, \
            list2cmdline, mswindows
    from kitchen.pycompat27.subprocess._subprocess import __all__
