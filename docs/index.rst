================================
Kitchen, everything but the sink
================================

:Author: Toshio Kuratomi
:Date: 20 May 2010
:Version: 0.1.x

We've all done it.  In the process of writing a brand new application we've
discovered that we need a little bit of code that we've invented before.
Perhaps it's something to handle unicode text.  Perhaps it's something to make
a bit of python-2.5 code run on python-2.3.  Whatever it is, it ends up being
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
using newer stdlib modules on older python versions, text manipulation,
PEP-386 versioning, and gettext.  With this package we're trying to provide
a few useful features that don't have too many dependencies outside of the
stdlib.  We'll be releasing other modules that drop into the kitchen namespace
to add other features (possibly with larger deps).

------------
Requirements
------------

kitchen requires

:python: 2.3.1 or later

Soft Requirements
=================

If found, these libraries will be used to make the implementation of something
better in some way.  If they are not present, the API that they enable will
still exist but may function in a different manner.

`chardet <http://chardet.feedparser.org/>`_
    Used in :func:`~kitchen.text.xml.guess_encoding__to_xml` to help guess
    encoding of byte strings being converted.  If not present, unknown
    encodings will be converted as if they were latin1

---------------------------
Other Recommended Libraries
---------------------------

These libraries implement commonly used functionality that everyone seems to
invent.  Rather than reinvent their wheel, I simply list the things that they
do well for now.  Perhaps if people can't find them normally, I'll add them as
requirements in setup.py or link them into kitchen's namespace.  For now, I
just mention them here:

`bunch <http://pypi.python.org/pypi/bunch/>`_
    Bunch is a dictionary that you can use attribute lookup as well as bracket
    notation to access.  Setting it apart from most homebrewed implementations
    is the bunchify() function which will descend nested structures of lists
    and dicts, transforming the dicts to Bunch's.
`hashlib <http://code.krypto.org/python/hashlib/>`_
    Python 2.5 and forward have a hashlib library that provides secure hash
    functions to python.  If you're developing for python2.3 or python2.4,
    though, you can install the standalone hashlib library and have access to
    the same functions.

-------
License
-------

This python module is distributed under the terms of the GNU General
Public License Version 2 or later.

.. note:: I'm currently working on getting permission from some people to
    relicense pieces this code to the LGPLv2+.  Once that is done, the library
    will be licensed in whole as the GNU Lesser General Public License Version
    2 or later.  New contributions to the library should be contributed under
    the LGPLv2+.

    The files with GPLv2+ code that still need to be relicensed are:

    * kitchen/text/utf8.py
    * i18n/__init__.py

.. note:: Some parts of this module are licensed under terms less restrictive
    than the GPL.  If you separate these files from the work as a whole you are
    allowed to use them under the less restrictive licenses.  The following is
    a list of the files that are known:

    `Python 2 license <http://www.python.org/download/releases/2.4/license/>`_
        subprocess.py and test_subprocess.py
    `LGPLv2+ <http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html>`_
        tests/* other than test_subprocess.py, files directly contained in
        kitchen/, kitchen/pycompat24/, kitchen/versioning/, and kitchen/text/
        except for utf8.py

--------
Contents
--------

.. toctree::
    :maxdepth: 2

    api-overview
    glossary

------------------
Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
