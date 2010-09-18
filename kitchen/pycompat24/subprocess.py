# :W0611, W0401: Rather than have two versions of subprocess, we import the python2.7
#   version here as well
#pylint:disable-msg=W0611,W0401
from kitchen.pycompat27.subprocess import *
import kitchen.pycompat27.subprocess.__all__
