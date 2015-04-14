""" BDD-like acceptance test.

This file is made available under the Creative Commons
CC0 1.0 Universal Public Domain Dedication.

The person who associated a work with this deed has dedicated the work to the
public domain by waiving all of his or her rights to the work worldwide under
copyright law, including all related and neighboring rights, to the extent
allowed by law. You can copy, modify, distribute and perform the work, even for
commercial purposes, all without asking permission.
"""

import unittest

from morelia import Parser

from calculator import Calculator


class CalculatorTestCase(unittest.TestCase):
    """ Calculator acceptance test case. """

    def setUp(self):
        self.calculator = Calculator()

    def step_I_have_powered_calculator_on(self):
        ur'I have powered calculator on'
        self.calculator.on()

    def step_I_enter_a_number_into_the_calculator(self, number):
        ur'I enter (\d+) into the calculator'  # match by regexp
        self.calculator.push(int(number))

    def step_I_press_add(self):  # matched by method name
        self.calculator.add()

    def step_the_result_should_be_on_the_screen(self, number):
        ur'the result should be {number} on the screen'  # match by format-like string
        assert int(number) == self.calculator.get_result()

    def test_addition(self):
        """ Addition feature """
        Parser().parse_file('calculator.feature').evaluate(self)


if __name__ == '__main__':  # pragma: nobranch
    unittest.main()
