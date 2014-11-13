# :W0401, W0611, W0614: Rather than have two versions of subprocess, we import
#   the python2.7 version here as well
#pylint:disable-msg=W0401,W0611,W0614
from kitchen.pycompat27.subprocess import *
from kitchen.pycompat27.subprocess import __all__
