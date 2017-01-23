"""TDD-like unit test.

This file is made available under the Creative Commons
CC0 1.0 Universal Public Domain Dedication.

The person who associated a work with this deed has dedicated the work to the
public domain by waiving all of his or her rights to the work worldwide under
copyright law, including all related and neighboring rights, to the extent
allowed by law. You can copy, modify, distribute and perform the work, even for
commercial purposes, all without asking permission.
"""
import unittest

from calculator import Calculator, CalculatorNotPoweredError


class CalculatorPushTestCase(unittest.TestCase):
    """Test :py:meth:`Calculator.push`."""

    def setUp(self):
        self.calculator = Calculator()

    def test_should_add_number_to_stack_if_powered(self):
        """Scenario: add number to stack."""
        # Arrange
        self.calculator.on()
        number = 50
        # Act
        self.calculator.push(number)
        # Assert
        self.assertEqual(self.calculator._stack, [number])

    def test_should_raise_exception_if_not_powered(self):
        """Scenario: not powered."""
        # Act & Assert
        self.assertRaises(CalculatorNotPoweredError, self.calculator.push, 50)

    def test_should_add_two_numbers_to_stack(self):
        """Scenario: add two numbers to stack."""
        # Arrange
        self.calculator.on()
        number1 = 50
        number2 = 70
        # Act
        self.calculator.push(number1)
        self.calculator.push(number2)
        # Assert
        self.assertEqual(self.calculator._stack, [number1, number2])


class CalculatorAddTestCase(unittest.TestCase):
    """Test :py:meth:`Calculator.add`."""

    def setUp(self):
        self.calculator = Calculator()

    def test_should_add_all_numbers_in_stack_if_powered(self):
        """Scenario: add all numbers."""
        # Arrange
        self.calculator.on()
        self.calculator.push(50)
        self.calculator.push(70)
        # Act
        self.calculator.add()
        # Assert
        self.assertEqual(self.calculator.get_result(), 120)

    def test_should_raise_exception_if_not_powered(self):
        """Scenario: not powered."""
        # Act & Assert
        self.assertRaises(CalculatorNotPoweredError, self.calculator.add)

    def test_should_return_0_if_empty_stack(self):
        """Scenario: empty stack."""
        # Arrange
        self.calculator.on()
        # Act
        self.calculator.add()
        # Assert
        self.assertEqual(self.calculator.get_result(), 0)


class CalculatorGetResultTestCase(unittest.TestCase):
    """Test :py:meth:`Calculator.get_result`."""

    def setUp(self):
        self.calculator = Calculator()

    def test_should_return_result(self):
        """Scenario: addition result present."""
        # Arrange
        self.calculator.on()
        self.calculator.push(50)
        self.calculator.push(70)
        self.calculator.add()
        # Act
        result = self.calculator.get_result()
        # Assert
        self.assertEqual(result, 120)

    def test_should_return_last_entered_value_if_no_operation_run(self):
        """Scenario: last result."""
        # Arrange
        self.calculator.on()
        self.calculator.push(50)
        self.calculator.push(70)
        # Act
        result = self.calculator.get_result()
        # Assert
        self.assertEqual(result, 70)

    def test_should_raise_exception_if_not_powered(self):
        """Scenario: not powered."""
        # Act & Assert
        self.assertRaises(CalculatorNotPoweredError, self.calculator.get_result)


class CalculatorOffTestCase(unittest.TestCase):
    """Test :py:meth:`Calculator.off`."""

    def setUp(self):
        self.calculator = Calculator()

    def test_should_raise_exception_if_number_entered_after_power_off(self):
        """Scenario: power off."""
        # Arrange
        self.calculator.on()
        self.calculator.push(50)
        self.calculator.off()
        # Act & Assert
        self.assertRaises(CalculatorNotPoweredError, self.calculator.push, 70)

    def test_should_have_empty_stack_after_on_push_off_on_cycle(self):
        """Scenario: on - push - off - on."""
        # Act
        self.calculator.on()
        self.calculator.push(50)
        self.calculator.off()
        self.calculator.on()
        # Assert
        self.assertEqual(self.calculator._stack, [])


if __name__ == '__main__':  # pragma: nobranch
    unittest.main()
