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

The :class:`DummyTranslations` object is an implementation detail that most
people don't need to know about.  It is a fallback in case no real translation
objects work on your system.  Unlike the :class:`gettext.NullTranslations`
object included in the |stdlib|_, :class:`DummyTranslations` makes sure that
any given function will only return byte :class:`str` or :class:`unicode`
strings.  No function will return both.

.. autoclass:: kitchen.i18n.DummyTranslations
    :members:
    :undoc-members:

