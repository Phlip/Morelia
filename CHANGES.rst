Version History
===============================================================================

Version: 0.5.1 (Unreleased)
-------------------------------------------------------------------------------

FIXED
^^^^^

  * bug with setUp/tearDown methods called twice
  * bug with double run of background steps when show_all_missing=True


Version: 0.5.0 (2015-05-30)
-------------------------------------------------------------------------------

ADDED
^^^^^

  * labels in feature files
  * tags decorator
  * step's text payload


Version: 0.4.2 (2015-05-10)
-------------------------------------------------------------------------------

FIXED
^^^^^

  * bug with matching utf-8 docstrings with unicode predicate


Version: 0.4.1 (2015-05-07)
-------------------------------------------------------------------------------

FIXED
^^^^^

  * bug with comments support in scenarios with tables


Version: 0.4.0 (2015-04-26)
-------------------------------------------------------------------------------

ADDED
^^^^^

  * support for Background keyword
  * support for different output formatters
  * Examples keyword as no-op

CHANGED
^^^^^^^

  * folding missing steps suggestions for more condense output

Version: 0.3.0 (2015-04-14)
-------------------------------------------------------------------------------

ADDED
^^^^^

  * support for matching methods by str.format-like ({name}) docstrings
  * example project

CHANGED
^^^^^^^

  * showing all missing steps instead of only first

Version: 0.2.1 (2015-04-06)
-------------------------------------------------------------------------------

ADDED
^^^^^

  * support for Python 3
  * native language support
