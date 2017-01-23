#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase

from mock import sentinel, Mock, patch

from morelia import run
from morelia.decorators import tags
from morelia.parser import Parser
from morelia.grammar import Morelia, Step
from morelia.exceptions import MissingStepError


@tags(['unit'])
class MoreliaReconstructionTestCase(TestCase):
    """ Test :py:meth:`Morelia.reconstruction`. """

    def test_should_reconstruct_unicode(self):
        """ Scenario: unicode input """
        # Arrange
        obj = Morelia('???', u'zażółć gęślą jaźń')
        # Act
        result = obj.reconstruction()
        # Assert
        self.assertEqual(result, u'???: zażółć gęślą jaźń\n')

    def test_should_reconstruct_utf8(self):
        """ Scenario: utf8 input """
        # Arrange
        obj = Morelia('???', 'zażółć gęślą jaźń')
        # Act
        result = obj.reconstruction()
        # Assert
        self.assertEqual(result, u'???: zażółć gęślą jaźń\n')


@tags(['unit'])
class MissingStepErrorTestCase(TestCase):
    """ Test :py:meth:`MissingStepError`. """

    def test_should_create_exception(self):
        """ Scenario: exception with step and suggest """
        # Arrange
        # Act
        result = MissingStepError('predicate line', 'def step_predicate_line(self):\n    pass', 'step_predicate_line', '')
        # Assert
        self.assertTrue(result is not None)
        self.assertEqual(result.predicate, 'predicate line')


@tags(['unit'])
class StepFindStepTestCase(TestCase):
    """ Test :py:meth:`Step.find_step`. """

    def test_should_find_method(self):
        """ Scenario: method found """
        # Arrange
        obj = Step('???', 'method')
        # Act
        matcher = Mock()
        matcher.find.return_value = (sentinel.method, [], {})
        result, args, kwargs = obj.find_step(matcher)
        # Assert
        self.assertEqual(result, sentinel.method)

    def test_should_not_find_method(self):
        """ Scenario: not found """
        # Arrange
        obj = Step('???', u'some_method')
        matcher = Mock()
        matcher.find.return_value = (None, [], {})
        matcher.suggest.return_value = ('suggest', 'method_name', 'docstring')
        self.assertRaises(MissingStepError, obj.find_step, matcher)


@tags(['unit'])
class RunTestCase(TestCase):
    """ Test :py:func:`run`. """

    @patch('morelia.has_color_support')
    @patch('morelia.PlainTextFormatter')
    @patch.object(Parser, 'parse_file')
    def test_should_parse_file_and_evaluate_tests(self, parse_file, PlainTextFormatter, has_color_support):
        """ Scenario: run and evaluate """
        has_color_support.return_value = False
        run(sentinel.filename, sentinel.suite)
        parse_file.assert_called_once_with(sentinel.filename)
        parse_file.return_value.evaluate.assert_called_once_with(
            sentinel.suite, show_all_missing=True)

    @patch('morelia.has_color_support')
    @patch('morelia.PlainTextFormatter')
    @patch.object(Parser, 'parse_file')
    def test_should_run_verbose_with_plain_text_formatter(self, parse_file, PlainTextFormatter, has_color_support):
        """ Scenario: run verbose on windows """
        has_color_support.return_value = False
        run(sentinel.filename, sentinel.suite, verbose=True)
        parse_file.assert_called_once_with(sentinel.filename)
        parse_file.return_value.evaluate.assert_called_once_with(
            sentinel.suite, formatter=PlainTextFormatter.return_value,
            show_all_missing=True)

    @patch('morelia.has_color_support')
    @patch('morelia.ColorTextFormatter')
    @patch.object(Parser, 'parse_file')
    def test_should_run_verbose_with_color_text_formatter(self, parse_file, ColorTextFormatter, has_color_support):
        """ Scenario: run verbose on systems with color support """
        has_color_support.return_value = True
        run(sentinel.filename, sentinel.suite, verbose=True)
        parse_file.assert_called_once_with(sentinel.filename)
        parse_file.return_value.evaluate.assert_called_once_with(
            sentinel.suite, formatter=ColorTextFormatter.return_value,
            show_all_missing=True)

    @patch.object(Parser, 'parse_file')
    def test_should_use_provided_formatter(self, parse_file):
        """ Scenario: run verbose on systems with color support """
        run(sentinel.filename, sentinel.suite, verbose=True, formatter=sentinel.formatter)
        parse_file.assert_called_once_with(sentinel.filename)
        parse_file.return_value.evaluate.assert_called_once_with(
            sentinel.suite, formatter=sentinel.formatter,
            show_all_missing=True)
