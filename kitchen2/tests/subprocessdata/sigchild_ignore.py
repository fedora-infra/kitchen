import os
import signal, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from kitchen.pycompat27.subprocess import _subprocess as subprocess

# On Linux this causes os.waitpid to fail with OSError as the OS has already
# reaped our child process.  The wait() passing the OSError on to the caller
# and causing us to exit with an error is what we are testing against.
signal.signal(signal.SIGCHLD, signal.SIG_IGN)
subprocess.Popen([sys.executable, '-c', 'print("albatross")']).wait()
