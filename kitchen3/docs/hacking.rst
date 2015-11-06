=======================================
Conventions for contributing to kitchen
=======================================

-----
Style
-----

* Strive to be :pep:`8` compliant
* Run `:command:`pylint` ` over the code and try to resolve most of its nitpicking

------------------------
Python 2.4 compatibility
------------------------

At the moment, we're supporting python-2.4 and above.  Understand that there's
a lot of python features that we cannot use because of this.

Sometimes modules in the |stdlib|_ can be added to kitchen so that they're
available.  When we do that we need to be careful of several things:

1. Keep the module in sync with the version in the python-2.x trunk.  Use
   :file:`maintainers/sync-copied-files.py` for this.
2. Sync the unittests as well as the module.
3. Be aware that not all modules are written to remain compatible with
   Python-2.4 and might use python language features that were not present
   then (generator expressions, relative imports, decorators, with, try: with
   both except: and finally:, etc)  These are not good candidates for
   importing into kitchen as they require more work to keep synced.

---------
Unittests
---------

* At least smoketest your code (make sure a function will return expected
  values for one set of inputs).
* Note that even 100% coverage is not a guarantee of working code!  Good tests
  will realize that you need to also give multiple inputs that test the code
  paths of called functions that are outside of your code.  Example::

        def to_unicode(msg, encoding='utf8', errors='replace'):
            return unicode(msg, encoding, errors)

        # Smoketest only.  This will give 100% coverage for your code (it
        # tests all of the code inside of to_unicode) but it leaves a lot of
        # room for errors as it doesn't test all combinations of arguments
        # that are then passed to the unicode() function.

        tools.ok_(to_unicode('abc') == u'abc')

        # Better -- tests now cover non-ascii characters and that error conditions
        # occur properly.  There's a lot of other permutations that can be
        # added along these same lines.
        tools.ok_(to_unicode(u'café', 'utf8', 'replace'))
        tools.assert_raises(UnicodeError, to_unicode, [u'cafè ñunru'.encode('latin1')])

* We're using nose for unittesting.  Rather than depend on unittest2
  functionality, use the functions that nose provides.
* Remember to maintain python-2.4 compatibility even in unittests.

----------------------------
Docstrings and documentation
----------------------------

We use sphinx to build our documentation.  We use the sphinx autodoc extension
to pull docstrings out of the modules for API documentation.  This means that
docstrings for subpackages and modules should follow a certain pattern.  The
general structure is:

* Introductory material about a module in the module's top level docstring.

  * Introductory material should begin with a level two title: an overbar and
    underbar of '-'.

* docstrings for every function.

  * The first line is a short summary of what the function does
  * This is followed by a blank line
  * The next lines are a `field list
    <http://sphinx.pocoo.org/markup/desc.html#info-field-lists>_` giving
    information about the function's signature.  We use the keywords:
    ``arg``, ``kwarg``, ``raises``, ``returns``, and sometimes ``rtype``.  Use
    these to describe all arguments, key word arguments, exceptions raised,
    and return values using these.

    * Parameters that are ``kwarg`` should specify what their default
      behaviour is.

.. _kitchen-versioning:

------------------
Kitchen versioning
------------------

Currently the kitchen library is in early stages of development.  While we're
in this state, the main kitchen library uses the following pattern for version
information:

* Versions look like this::
    __version_info__ = ((0, 1, 2),)
    __version__ = '0.1.2'

* The Major version number remains at 0 until we decide to make the first 1.0
  release of kitchen.  At that point, we're declaring that we have some
  confidence that we won't need to break backwards compatibility for a while.
* The Minor version increments for any backwards incompatible API changes.
  When this is updated, we reset micro to zero.
* The Micro version increments for any other changes (backwards compatible API
  changes, pure bugfixes, etc).

.. note::

    Versioning is only updated for releases that generate sdists and new
    uploads to the download directory.  Usually we update the version
    information for the library just before release.  By contrast, we update
    kitchen :ref:`subpackage-versioning` when an API change is made.  When in
    doubt, look at the version information in the last release.

----
I18N
----

All strings that are used as feedback for users need to be translated.
:mod:`kitchen` sets up several functions for this.  :func:`_` is used for
marking things that are shown to users via print, GUIs, or other "standard"
methods.  Strings for exceptions are marked with :func:`b_`.  This function
returns a byte :class:`str` which is needed for use with exceptions::

    from kitchen import _, b_

    def print_message(msg, username):
        print _('%(user)s, your message of the day is:  %(message)s') % {
                'message': msg, 'user': username}

        raise Exception b_('Test message')

This serves several purposes:

* It marks the strings to be extracted by an xgettext-like program.
* :func:`_` is a function that will substitute available translations at
  runtime.

.. note::

    By using the ``%()s with dict`` style of string formatting, we make this
    string friendly to translators that may need to reorder the variables when
    they're translating the string.

`paver <http://www.blueskyonmars.com/projects/paver/>_` and `babel
<http://babel.edgewall.org/>_` are used to extract the strings.

-----------
API updates
-----------

Kitchen strives to have a long deprecation cycle so that people have time to
switch away from any APIs that we decide to discard.  Discarded APIs should
raise a :exc:`DeprecationWarning` and clearly state in the warning message and
the docstring how to convert old code to use the new interface.  An example of
deprecating a function::

    import warnings

    from kitchen import _
    from  kitchen.text.converters import to_bytes, to_unicode
    from kitchen.text.new_module import new_function

    def old_function(param):
        '''**Deprecated**

        This function is deprecated.  Use
        :func:`kitchen.text.new_module.new_function` instead. If you want
        unicode strngs as output, switch to::

            >>> from kitchen.text.new_module import new_function
            >>> output = new_function(param)

        If you want byte strings, use::

            >>> from kitchen.text.new_module import new_function
            >>> from kitchen.text.converters import to_bytes
            >>> output = to_bytes(new_function(param))
        '''
        warnings.warn(_('kitchen.text.old_function is deprecated.  Use'
            ' kitchen.text.new_module.new_function instead'),
            DeprecationWarning, stacklevel=2)

        as_unicode = isinstance(param, unicode)
        message = new_function(to_unicode(param))
        if not as_unicode:
            message = to_bytes(message)
        return message

If a particular API change is very intrusive, it may be better to create a new
version of the subpackage and ship both the old version and the new version.

---------
NEWS file
---------

Update the :file:`NEWS` file when you make a change that will be visible to
the users.  This is not a ChangeLog file so we don't need to list absolutely
everything but it should give the user an idea of how this version differs
from prior versions.  API changes should be listed here explicitly.  bugfixes
can be more general::

    -----
    0.2.0
    -----
    * Relicense to LGPLv2+
    * Add kitchen.text.format module with the following functions:
      textual_width, textual_width_chop.
    * Rename the kitchen.text.utils module to kitchen.text.misc.  use of the
      old names is deprecated but still available.
    * bugfixes applied to kitchen.pycompat24.defaultdict that fixes some
      tracebacks

-------------------
Kitchen subpackages
-------------------

Kitchen itself is a namespace.  The kitchen sdist (tarball) provides certain
useful subpackages.

.. seealso::

    `Kitchen addon packages`_
        For information about subpackages not distributed in the kitchen sdist
        that install into the kitchen namespace.

.. _subpackage-versioning:

Versioning
==========

Each subpackage should have its own version information which is independent
of the other kitchen subpackages and the main kitchen library version. This is
used so that code that depends on kitchen APIs can check the version
information.  The standard way to do this is to put something like this in the
subpackage's :file:`__init__.py`::

    from kitchen.versioning import version_tuple_to_string

    __version_info__ = ((1, 0, 0),)
    __version__ = version_tuple_to_string(__version_info__)

:attr:`__version_info__` is documented in :mod:`kitchen.versioning`.  The
values of the first tuple should describe API changes to the module.  There
are at least three numbers present in the tuple: (Major, minor, micro).  The
major version number is for backwards incompatible changes (For
instance, removing a function, or adding a new mandatory argument to
a function).  Whenever one of these occurs, you should increment the major
number and reset minor and micro to zero.  The second number is the minor
version.  Anytime new but backwards compatible changes are introduced this
number should be incremented and the micro version number reset to zero.  The
micro version should be incremented when a change is made that does not change
the API at all.  This is a common case for bugfixes, for instance.

Version information beyond the first three parts of the first tuple may be
useful for versioning but semantically have similar meaning to the micro
version.

.. note::

    We update the :attr:`__version_info__` tuple when the API is updated.
    This way there's less chance of forgetting to update the API version when
    a new release is made.  However, we try to only increment the version
    numbers a single step for any release.  So if kitchen-0.1.0 has
    kitchen.text.__version__ == '1.0.1', kitchen-0.1.1 should have
    kitchen.text.__version__ == '1.0.2' or '1.1.0' or '2.0.0'.

Criteria for subpackages in kitchen
===================================

Supackages within kitchen should meet these criteria:

* Generally useful or needed for other pieces of kitchen.

* No mandatory requirements outside of the |stdlib|_.

  * Optional requirements from outside the |stdlib|_ are allowed.  Things with
    mandatory requirements are better placed in `kitchen addon packages`_

* Somewhat API stable -- this is not a hard requirement.  We can change the
  kitchen api.  However, it is better not to as people may come to depend on
  it.

  .. seealso::

    `API Updates`_

----------------------
Kitchen addon packages
----------------------

Addon packages are very similar to subpackages integrated into the kitchen
sdist.  This section just lists some of the differences to watch out for.

setup.py
========

Your :file:`setup.py` should contain entries like this::

    # It's suggested to use a dotted name like this so the package is easily
    # findable on pypi:
    setup(name='kitchen.config',
        # Include kitchen in the keywords, again, for searching on pypi
        keywords=['kitchen', 'configuration'],
        # This package lives in the directory kitchen/config
        packages=['kitchen.config'],
        # [...]
    )

Package directory layout
========================

Create a :file:`kitchen` directory in the toplevel.  Place the addon
subpackage in there.  For example::

  ./                     <== toplevel with README, setup.py, NEWS, etc
  kitchen/
  kitchen/__init__.py
  kitchen/config/        <== subpackage directory
  kitchen/config/__init__.py

Fake kitchen module
===================

The :file::`__init__.py` in the :file:`kitchen` directory is special.  It
won't be installed.  It just needs to pull in the kitchen from the system so
that you are able to test your module.  You should be able to use this
boilerplate::

    # Fake module.  This is not installed,  It's just made to import the real
    # kitchen modules for testing this module
    import pkgutil

    # Extend the __path__ with everything in the real kitchen module
    __path__ = pkgutil.extend_path(__path__, __name__)

.. note::

    :mod:`kitchen` needs to be findable by python for this to work.  Installed
    in the :file:`site-packages` directory or adding it to the
    :envvar:`PYTHONPATH` will work.

Your unittests should now be able to find both your submodule and the main
kitchen module.

Versioning
==========

It is recommended that addon packages version similarly to
:ref:`subpackage-versioning`.  The :data:`__version_info__` and
:data:`__version__` strings can be changed independently of  the version
exposed by setup.py so that you have both an API version
(:data:`__version_info__`) and release version that's easier for people to
parse.  However, you aren't required to do this and you could follow
a different methodology if you want (for instance, :ref:`kitchen-versioning`)
