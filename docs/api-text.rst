=============================================
Kitchen.text: unicode and utf8 and xml oh my!
=============================================

.. contents::

.. toctree::
    :hidden:

    api-text-converters

--------------------------
unicode and str conversion
--------------------------

These are function for converting between unicode, bytes, and xml.

:ref:`kitchen.text.converters`

-------
display
-------

.. automodule:: kitchen.text.display
    :members:

-----
UTF-8
-----

.. automodule:: kitchen.text.utf8
    :members:
    :deprecated:

Internal Data
=============

There are a few internal functions and variables in this module.  Code outside
of kitchen shouldn't use them but people coding on kitchen itself may find
them useful.

.. autodata:: kitchen.text.display._COMBINING

.. autofunction:: kitchen.text.display._interval_bisearch

.. autofunction:: kitchen.text.display._generate_combining_table

----
Misc
----

.. automodule:: kitchen.text.misc
    :members:

----------
Exceptions
----------

 .. automodule:: kitchen.text.exceptions
    :members:
