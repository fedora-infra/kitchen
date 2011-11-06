===================
1.0.0 Porting Guide
===================

The 0.1 through 1.0.0 releases focused on bringing in functions from yum and
python-fedora.  This porting guide tells how to port from those APIs to their
kitchen replacements.

-------------
python-fedora
-------------

===================================  ===================
python-fedora                        kitchen replacement
-----------------------------------  -------------------
:func:`fedora.iterutils.isiterable`  :func:`kitchen.iterutils.isiterable` [#f1]_
:func:`fedora.textutils.to_unicode`  :func:`kitchen.text.converters.to_unicode`
:func:`fedora.textutils.to_bytes`    :func:`kitchen.text.converters.to_bytes`
===================================  ===================

.. [#f1] :func:`~kitchen.iterutils.isiterable` has changed slightly in
    kitchen.  The :attr:`include_string` attribute has switched its default value
    from :data:`True` to :data:`False`.  So you need to change code like::

        >>> # Old code
        >>> isiterable('abcdef')
        True
        >>> # New code
        >>> isiterable('abcdef', include_string=True)
        True

---
yum
---

=================================  ===================
yum                                kitchen replacement
---------------------------------  -------------------
:func:`yum.i18n.dummy_wrapper`     :meth:`kitchen.i18n.DummyTranslations.ugettext` [#y1]_
:func:`yum.i18n.dummyP_wrapper`    :meth:`kitchen.i18n.DummyTanslations.ungettext` [#y1]_
:func:`yum.i18n.utf8_width`        :func:`kitchen.text.display.textual_width`
:func:`yum.i18n.utf8_width_chop`   :func:`kitchen.text.display.textual_width_chop`
                                   and :func:`kitchen.text.display.textual_width` [#y2]_ [#y4]_
:func:`yum.i18n.utf8_valid`        :func:`kitchen.text.misc.byte_string_valid_encoding`
:func:`yum.i18n.utf8_text_wrap`    :func:`kitchen.text.display.wrap` [#y3]_
:func:`yum.i18n.utf8_text_fill`    :func:`kitchen.text.display.fill` [#y3]_
:func:`yum.i18n.to_unicode`        :func:`kitchen.text.converters.to_unicode` [#y5]_
:func:`yum.i18n.to_unicode_maybe`  :func:`kitchen.text.converters.to_unicode` [#y5]_
:func:`yum.i18n.to_utf8`           :func:`kitchen.text.converters.to_bytes` [#y5]_
:func:`yum.i18n.to_str`            :func:`kitchen.text.converters.to_unicode`
                                   or :func:`kitchen.text.converters.to_bytes` [#y6]_
:func:`yum.i18n.str_eq`            :func:`kitchen.text.misc.str_eq`
:func:`yum.misc.to_xml`             :func:`kitchen.text.converters.unicode_to_xml`
                                    or :func:`kitchen.text.converters.byte_string_to_xml` [#y7]_
:func:`yum.i18n._`                 See: :ref:`yum-i18n-init`
:func:`yum.i18n.P_`                See: :ref:`yum-i18n-init`
:func:`yum.i18n.exception2msg`      :func:`kitchen.text.converters.exception_to_unicode`
                                    or :func:`kitchen.text.converter.exception_to_bytes` [#y8]_
=================================  ===================

.. [#y1] These yum methods provided fallback support for :mod:`gettext`
    functions in case either ``gaftonmode`` was set or :mod:`gettext` failed
    to return an object.  In kitchen, we can use the
    :class:`kitchen.i18n.DummyTranslations` object to fulfill that role.
    Please see :ref:`yum-i18n-init` for more suggestions on how to do this.

.. [#y2] The yum version of these functions returned a byte :class:`str`.  The
    kitchen version listed here returns a :class:`unicode` string.  If you
    need a byte :class:`str` simply call
    :func:`kitchen.text.converters.to_bytes` on the result.

.. [#y3] The yum version of these functions would return either a byte
    :class:`str` or a :class:`unicode` string depending on what the input
    value was.  The kitchen version always returns :class:`unicode` strings.

.. [#y4] :func:`yum.i18n.utf8_width_chop` performed two functions.  It
    returned the piece of the message that fit in a specified width and the
    width of that message.  In kitchen, you need to call two functions, one
    for each action::

        >>> # Old way
        >>> utf8_width_chop(msg, 5)
        (5, 'く ku')
        >>> # New way
        >>> from kitchen.text.display import textual_width, textual_width_chop
        >>> (textual_width(msg), textual_width_chop(msg, 5))
        (5, u'く ku')

.. [#y5] If the yum version of :func:`~yum.i18n.to_unicode` or
    :func:`~yum.i18n.to_utf8` is given an object that is not a string, it
    returns the object itself.  :func:`kitchen.text.converters.to_unicode` and
    :func:`kitchen.text.converters.to_bytes` default to returning the
    ``simplerepr`` of the object instead.  If you want the yum behaviour, set
    the :attr:`nonstring` parameter to ``passthru``::

        >>> from kitchen.text.converters import to_unicode
        >>> to_unicode(5)
        u'5'
        >>> to_unicode(5, nonstring='passthru')
        5

.. [#y6] :func:`yum.i18n.to_str` could return either a byte :class:`str`.  or
    a :class:`unicode` string In kitchen you can get the same effect but you
    get to choose whether you want a byte :class:`str` or a :class:`unicode`
    string.  Use :func:`~kitchen.text.converters.to_bytes` for :class:`str`
    and :func:`~kitchen.text.converters.to_unicode` for :class:`unicode`.

.. [#y7] :func:`yum.misc.to_xml` was buggy as written.  I think the intention
    was for you to be able to pass a byte :class:`str` or :class:`unicode`
    string in and get out a byte :class:`str` that was valid to use in an xml
    file.  The two kitchen functions
    :func:`~kitchen.text.converters.byte_string_to_xml` and
    :func:`~kitchen.text.converters.unicode_to_xml` do that for each string
    type.

.. [#y8] When porting :func:`yum.i18n.exception2msg` to use kitchen, you
    should setup two wrapper functions to aid in your port.  They'll look like
    this:

    .. code-block:: python

        from kitchen.text.converters import EXCEPTION_CONVERTERS, \
            BYTE_EXCEPTION_CONVERTERS, exception_to_unicode, \
            exception_to_bytes
        def exception2umsg(e):
            '''Return a unicode representation of an exception'''
            c = [lambda e: e.value]
            c.extend(EXCEPTION_CONVERTERS)
            return exception_to_unicode(e, converters=c)
        def exception2bmsg(e):
            '''Return a utf8 encoded str representation of an exception'''
            c = [lambda e: e.value]
            c.extend(BYTE_EXCEPTION_CONVERTERS)
            return exception_to_bytes(e, converters=c)

    The reason to define this wrapper is that many of the exceptions in yum
    put the message in the :attr:`value` attribute of the :exc:`Exception`
    instead of adding it to the :attr:`args` attribute.  So the default
    :data:`~kitchen.text.converters.EXCEPTION_CONVERTERS` don't know where to
    find the message.  The wrapper tells kitchen to check the :attr:`value`
    attribute for the message.  The reason to define two wrappers may be less
    obvious.  :func:`yum.i18n.exception2msg` can return a :class:`unicode`
    string or a byte :class:`str` depending on a combination of what
    attributes are present on the :exc:`Exception` and what locale the
    function is being run in.  By contrast,
    :func:`kitchen.text.converters.exception_to_unicode` only returns
    :class:`unicode` strings and
    :func:`kitchen.text.converters.exception_to_bytes` only returns byte
    :class:`str`.  This is much safer as it keeps code that can only handle
    :class:`unicode` or only handle byte :class:`str` correctly from getting
    the wrong type when an input changes but it means you need to examine the
    calling code when porting from :func:`yum.i18n.exception2msg` and use the
    appropriate wrapper.

.. _yum-i18n-init:

Initializing Yum i18n
=====================

Previously, yum had several pieces of code to initialize i18n.  From the
toplevel of :file:`yum/i18n.py`::

    try:.
        '''
        Setup the yum translation domain and make _() and P_() translation wrappers
        available.
        using ugettext to make sure translated strings are in Unicode.
        '''
        import gettext
        t = gettext.translation('yum', fallback=True)
        _ = t.ugettext
        P_ = t.ungettext
    except:
        '''
        Something went wrong so we make a dummy _() wrapper there is just
        returning the same text
        '''
        _ = dummy_wrapper
        P_ = dummyP_wrapper

With kitchen, this can be changed to this::

    from kitchen.i18n import easy_gettext_setup, DummyTranslations
    try:
        _, P_ = easy_gettext_setup('yum')
    except:
        translations = DummyTranslations()
        _ = translations.ugettext
        P_ = translations.ungettext

.. note:: In :ref:`overcoming-frustration`, it is mentioned that for some
    things (like exception messages), using the byte :class:`str` oriented
    functions is more appropriate.  If this is desired, the setup portion is
    only a second call to :func:`kitchen.i18n.easy_gettext_setup`::

        b_, bP_ = easy_gettext_setup('yum', use_unicode=False)

The second place where i18n is setup is in :meth:`yum.YumBase._getConfig` in
:file:`yum/__init_.py` if ``gaftonmode`` is in effect::

    if startupconf.gaftonmode:
        global _
        _ = yum.i18n.dummy_wrapper

This can be changed to::

    if startupconf.gaftonmode:
        global _
        _ = DummyTranslations().ugettext()
