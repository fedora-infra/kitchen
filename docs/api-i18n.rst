===================
Kitchen.i18n Module
===================

.. automodule:: kitchen.i18n

Functions
=========

:func:`easy_gettext_setup` should satisfy the needs of most users.
:func:`get_translation_object` is designed to ease the way for anyone that
needs more control.

.. autofunction:: easy_gettext_setup

.. autofunction:: get_translation_object

Translation Objects
===================

The standard translation objects from the :mod:`gettext` module suffer from
several problems:

* They can throw :exc:`UnicodeError`
* They can't find translations for non-:term:`ASCII` byte :class:`str`
  messages
* They may return either :class:`unicode` string or byte :class:`str` from the
  same function even though the functions say they will only return
  :class:`unicode` or only return byte :class:`str`.

:class:`DummyTranslations` and :class:`NewGNUTranslations` were written to fix
these issues.

.. autoclass:: kitchen.i18n.DummyTranslations
    :members:

.. autoclass:: kitchen.i18n.NewGNUTranslations
    :members:
