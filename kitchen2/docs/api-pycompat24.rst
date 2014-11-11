=======================
Python 2.4 Compatibiity
=======================


-------------------
Sets for python-2.3
-------------------

.. automodule:: kitchen.pycompat24.sets
.. autofunction:: kitchen.pycompat24.sets.add_builtin_set

----------------------------------
Partial new style base64 interface
----------------------------------

.. automodule:: kitchen.pycompat24.base64
    :members:

----------
Subprocess
----------

.. seealso::

    :mod:`kitchen.pycompat27.subprocess`
        Kitchen includes the python-2.7 version of subprocess which has a new
        function, :func:`~kitchen.pycompat27.subprocess.check_output`.  When
        you import :mod:`pycompat24.subprocess` you will be getting the
        python-2.7 version of subprocess rather than the 2.4 version (where
        subprocess first appeared).  This choice was made so that we can
        concentrate our efforts on keeping the single version of subprocess up
        to date rather than working on a 2.4 version that very few people
        would need specifically.
