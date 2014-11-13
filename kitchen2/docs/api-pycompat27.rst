========================
Python 2.7 Compatibility
========================

.. module:: kitchen.pycompat27.subprocess

--------------------------
Subprocess from Python 2.7
--------------------------

The :mod:`subprocess` module included here is a direct import from
python-2.7's |stdlib|_.  You can access it via::

    >>> from kitchen.pycompat27 import subprocess

The motivation for including this module is that various API changing
improvements have been made to subprocess over time.  The following is a list
of the known changes to :mod:`subprocess` with the python version they were
introduced in:

====================================  ===
New API Feature                       Ver
====================================  ===
:exc:`subprocess.CalledProcessError`  2.5
:func:`subprocess.check_call`         2.5
:func:`subprocess.check_output`       2.7
:meth:`subprocess.Popen.send_signal`  2.6
:meth:`subprocess.Popen.terminate`    2.6
:meth:`subprocess.Popen.kill`         2.6
====================================  ===

.. seealso::

    The stdlib :mod:`subprocess` documenation
        For complete documentation on how to use subprocess
