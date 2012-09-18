* Update documentation
  * Information about exceptions can be changed -- exceptions now take unicode (str)  just fine
  * byte string needs to be updated to bytes/bytearray and unicode string to str
  * What about getwrier?
* Switch exceptions to use str instead of bytes for translations
* Make PendingDeprecationWarnings for pycompat* and StrictDict
  * Message should say that these are available in all Python3 versions.
    Use the stdlib version once the codebase no longer needs to run on py2

Audited files

[X} text/converters.py
[X] text/misc.py
[X] text/display.py
[X] versioning/__init__.py
[X] iterutils/__init__.py
[X] i18n/__init__.py
[X] text/utf8.py

[_] pycompat*  => just need deprecationwarnings
[X] collections/strictdict.py just need deprecationwarnings

(Other random __init__.py, release.py)

Python2 and python3

[X] Switch from isinstance(str, unicode, basestring) to kitchen.text.misc.is*string() functions to make porting easier
* Remove translations of exceptions?
* Switch unittests to not use ok_

Some design decisions:

* i18n:
  * DummyTranslations, NewGNUTranslations
    * These retain the python2 API of (gettext, lgettext), (ugettext)
    [_] Issue a PendingDeprecationWarning when used
  [X] Added a parameter to DummyTranslations and NewGNUTranslations: python2_api()
    [_] Need to add documentation on python2_api parameter as that is not in the stdlib gettext api
    * When True (default), uses python2 gettext api.  When false, uses python3 gettext api
  * Rationale: people that are doing a straight port might be depending on the
    various methods and behaviours (of gettext returning bytes).  So we want to
    retain that.  Howver, the python3 API is different and we should provide a
    native object for that.

* iterutils isiterable => include_string will count both str and (bytes, bytearray).  
  * rationale: the include_string argument is to make this mistake
    obvious:  for i in b'abc': pass
    The bytes() object is really intended to be treated as a single object, not
    as a container there.

* collections/strictdict
* pycompat*  => these just point at their python3 stdlib implementations and
  issue a PendingDeprecationWarning if used.
  * Rationale: In the python3 version, these have no use.
  * PendingDeprecationWarning was used in python2 to flag something that
    wouldn't be deprecated in python2 but would be obsolete in python3.

* Documentation: the behvaiour of iter(b'string') is different than
  iter('string').  This causes iterutils.iterate() to do something different
