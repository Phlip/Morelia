# -*- coding: utf-8 -*-
"""
Running
=======

To run scenarios Morelia's :py:func:`run` method needs to be given at least
two parameters:

    * file name with scenarios description
    * TestCase with defined steps

Then running is as simple as:

.. code-block:: python

    run('calculator.feature', test_case_with_steps)

"""

import sys

from morelia.formatters import PlainTextFormatter, ColorTextFormatter
from morelia.parser import Parser  # noqa

__version__ = "0.8.0"


def has_color_support():
    """Check if color in terminal is supported."""
    return sys.platform != "win32"  # pragma: nocover


def run(
    filename,
    suite,
    as_str=None,
    scenario=r".*",
    verbose=False,
    show_all_missing=True,
    **kwargs
):  # NOQA
    """Parse file and run tests on given suite.

    :param str filename: file name
    :param unittest.TestCase suite: TestCase instance
    :param string as_str: None to use file or a string containing the feature to parse
    :param string scenario: a regex pattern to match the scenario to run
    :param boolean verbose: be verbose
    :param boolean show_all_missing: show all missing steps
    """
    formatter = kwargs.get("formatter", None)
    if verbose and not formatter:
        if has_color_support():
            formatter = ColorTextFormatter()
        else:
            formatter = PlainTextFormatter()
        kwargs["formatter"] = formatter
    kwargs["show_all_missing"] = show_all_missing
    parser = Parser()
    ast = (
        parser.parse_file(filename, scenario=scenario)
        if as_str is None
        else parser.parse_as_str(filename, as_str, scenario=scenario)
    )
    return ast.evaluate(suite, **kwargs)


__all__ = ("Parser", "run")
