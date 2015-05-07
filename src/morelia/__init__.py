# -*- coding: utf-8 -*-
import sys

from .formatters import PlainTextFormatter, ColorTextFormatter
from .parser import Parser  # noqa

__version__ = '0.4.1'


def has_color_support():
    return sys.platform != 'win32'  # pragma: nocover


def run(filename, suite, verbose=False, **kwargs):
    ''' Parse file and run tests on given suite.

    :param str filename: file name
    :param unittest.TestCase suite: TestCase instance
    :param boolean verbose: be verbose
    '''
    formatter = kwargs.get('formatter', None)
    if verbose and not formatter:
        if has_color_support():
            formatter = ColorTextFormatter()
        else:
            formatter = PlainTextFormatter()
        kwargs['formatter'] = formatter
    parser = Parser()
    ast = parser.parse_file(filename)
    return ast.evaluate(suite, **kwargs)


__all__ = ['Parser', 'run']
