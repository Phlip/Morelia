'''
Feature: Addition
    In order to avoid silly mistakes
    As a math idiot
    I want to be told the sum of two numbers

Scenario: Add two numbers
    Given I have powered calculator on
    When I enter "50" into the calculator
    And I enter "70" into the calculator
    And I press add
    Then the result should be "120" on the screen

Scenario: Subsequent additions
    Given I have powered calculator on
    When I enter "50" into the calculator
    And I enter "70" into the calculator
    And I press add
    And I enter "20" into the calculator
    And I press add
    Then the result should be "140" on the screen

Scenario: Add two numbers - table
    Given I have powered calculator on
    When I enter "<num1>" into the calculator
    And I enter "<num2>" into the calculator
    And I press add
    Then the result should be "<result>" on the screen
        | num1 | num2 | result |
        | 2    | 3    | 5      |
        | 4    | 5    | 9      |
'''

import os
import unittest

from morelia import run

from calculator import Calculator


class CalculatorDocstringTestCase(unittest.TestCase):
    """Calculator acceptance test case."""
    def test_addition(self):
        """Addition feature."""
        morelia.run(__file__, self, as_str=__doc__, verbose=True)

    def setUp(self):
        self.calculator = Calculator()

    def step_I_have_powered_calculator_on(self):
        r'I have powered calculator on'
        self.calculator.on()

    def step_I_enter_a_number_into_the_calculator(self, number):
        r'I enter "(.+)" into the calculator'  # match by regexp
        self.calculator.push(int(number))

    def step_I_press_add(self):  # matched by method name
        self.calculator.add()

    def step_the_result_should_be_on_the_screen(self, number):
        r'the result should be "{number}" on the screen'  # match by format-like string
        self.assertEqual(int(number), self.calculator.get_result())


if __name__ == '__main__':  # pragma: nobranch
    unittest.main()
