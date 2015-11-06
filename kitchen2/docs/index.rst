================================
Kitchen, everything but the sink
================================

:Author: Toshio Kuratomi
:Date: 19 March 2011
:Version: 1.0.x

We've all done it.  In the process of writing a brand new application we've
discovered that we need a little bit of code that we've invented before.
Perhaps it's something to handle unicode text.  Perhaps it's something to make
a bit of python-2.5 code run on python-2.4.  Whatever it is, it ends up being
a tiny bit of code that seems too small to worry about pushing into its own
module so it sits there, a part of your current project, waiting to be cut and
pasted into your next project.  And the next.  And the next.  And since that
little bittybit of code proved so useful to you, it's highly likely that it
proved useful to someone else as well.  Useful enough that they've written it
and copy and pasted it over and over into each of their new projects.

Well, no longer!  Kitchen aims to pull these small snippets of code into a few
python modules which you can import and use within your project.  No more copy
and paste!  Now you can let someone else maintain and release these small
snippets so that you can get on with your life.

This package forms the core of Kitchen.  It contains some useful modules for
using newer |stdlib|_ modules on older python versions, text manipulation,
:pep:`386` versioning, and initializing :mod:`gettext`.  With this package we're
trying to provide a few useful features that don't have too many dependencies
outside of the |stdlib|_.  We'll be releasing other modules that drop into the
kitchen namespace to add other features (possibly with larger deps) as time
goes on.

------------
Requirements
------------

We've tried to keep the core kitchen module's requirements lightweight.  At the
moment kitchen only requires

:python: 2.4 or later

.. warning:: Kitchen-1.1.0 was the last release that supported python-2.3.x

Soft Requirements
=================

If found, these libraries will be used to make the implementation of some part
of kitchen better in some way.  If they are not present, the API that they
enable will still exist but may function in a different manner.

`chardet <http://pypi.python.org/pypi/chardet>`_
    Used in :func:`~kitchen.text.misc.guess_encoding` and
    :func:`~kitchen.text.converters.guess_encoding_to_xml` to help guess
    encoding of byte strings being converted.  If not present, unknown
    encodings will be converted as if they were ``latin1``

---------------------------
Other Recommended Libraries
---------------------------

These libraries implement commonly used functionality that everyone seems to
invent.  Rather than reinvent their wheel, I simply list the things that they
do well for now.  Perhaps if people can't find them normally, I'll add them as
requirements in :file:`setup.py` or link them into kitchen's namespace.  For
now, I just mention them here:

`bunch <http://pypi.python.org/pypi/bunch/>`_
    Bunch is a dictionary that you can use attribute lookup as well as bracket
    notation to access.  Setting it apart from most homebrewed implementations
    is the :func:`bunchify` function which will descend nested structures of
    lists and dicts, transforming the dicts to Bunch's.
`hashlib <http://code.krypto.org/python/hashlib/>`_
    Python 2.5 and forward have a :mod:`hashlib` library that provides secure
    hash functions to python.  If you're developing for python2.4 though, you
    can install the standalone hashlib library and have access to the same
    functions.
`iterutils <http://pypi.python.org/pypi/iterutils/>`_
    The python documentation for :mod:`itertools` has some examples
    of other nice iterable functions that can be built from the
    :mod:`itertools` functions.  This third-party module creates those recipes
    as a module.
`ordereddict <http://pypi.python.org/pypi/ordereddict/>`_
    Python 2.7 and forward have a :mod:`~collections.OrderedDict` that
    provides a :class:`dict` whose items are ordered (and indexable) as well
    as named.
`unittest2 <http://pypi.python.org/pypi/unittest2>`_
    Python 2.7 has an updated :mod:`unittest` library with new functions not
    present in the |stdlib|_ for Python 2.6 or less.  If you want to use those
    new functions but need your testing framework to be compatible with older
    Python the unittest2 library provides the update as an external module.
`nose <http://somethingaboutorange.com/mrl/projects/nose/>`_
    If you want to use a test discovery tool instead of the unittest
    framework, nosetests provides a simple to use way to do that.

-------
License
-------

This python module is distributed under the terms of the
`GNU Lesser General Public License Version 2 or later
<http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html>`_.

.. note:: Some parts of this module are licensed under terms less restrictive
    than the LGPLv2+.  If you separate these files from the work as a whole
    you are allowed to use them under the less restrictive licenses.  The
    following is a list of the files that are known:

    `Python 2 license <http://www.python.org/download/releases/2.4/license/>`_
        :file:`_subprocess.py`, :file:`test_subprocess.py`,
        :file:`defaultdict.py`, :file:`test_defaultdict.py`,
        :file:`_base64.py`, and :file:`test_base64.py`

--------
Contents
--------

.. toctree::
    :maxdepth: 2

    tutorial
    api-overview
    porting-guide-0.3
    hacking
    glossary

------------------
Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

-------------
Project Pages
-------------

More information about the project can be found on the |projpage|_

The latest published version of this documentation can be found on the |docpage|_
