""" Toy calculator.

This file is made available under the Creative Commons
CC0 1.0 Universal Public Domain Dedication.

The person who associated a work with this deed has dedicated the work to the
public domain by waiving all of his or her rights to the work worldwide under
copyright law, including all related and neighboring rights, to the extent
allowed by law. You can copy, modify, distribute and perform the work, even for
commercial purposes, all without asking permission.
"""


class CalculatorNotPoweredError(Exception):
    pass


class Calculator(object):
    """ Calculator. """

    def __init__(self):
        self._powered = False

    def on(self):
        self._powered = True
        self._stack = []

    def off(self):
        self._powered = False

    def push(self, number):
        if not self._powered:
            raise CalculatorNotPoweredError
        self._stack.append(number)

    def add(self):
        if not self._powered:
            raise CalculatorNotPoweredError
        self._stack = [sum(self._stack)]

    def get_result(self):
        if not self._powered:
            raise CalculatorNotPoweredError
        return self._stack[-1]
