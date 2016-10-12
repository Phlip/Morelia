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

from .formatters import PlainTextFormatter, ColorTextFormatter
from .parser import Parser  # noqa

__version__ = '0.6.5'


def has_color_support():
    """Check if color in terminal is supported."""

    return sys.platform != 'win32'  # pragma: nocover


def run(filename, suite, verbose=False, show_all_missing=True, **kwargs):
    """ Parse file and run tests on given suite.

    :param str filename: file name
    :param unittest.TestCase suite: TestCase instance
    :param boolean verbose: be verbose
    :param boolean show_all_missing: show all missing steps
    """
    formatter = kwargs.get('formatter', None)
    if verbose and not formatter:
        if has_color_support():
            formatter = ColorTextFormatter()
        else:
            formatter = PlainTextFormatter()
        kwargs['formatter'] = formatter
    kwargs['show_all_missing'] = show_all_missing
    parser = Parser()
    ast = parser.parse_file(filename)
    return ast.evaluate(suite, **kwargs)


__all__ = ('Parser', 'run')
