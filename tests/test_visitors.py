import unittest
from collections import OrderedDict
from mock import Mock, sentinel, ANY

from morelia.decorators import tags
from morelia.exceptions import MissingStepError
from morelia.grammar import Step
from morelia.visitors import StepMatcherVisitor, TestVisitor


@tags(['unit'])
class StepMatcherVisitorVisitTestCase(unittest.TestCase):
    """ Test :py:meth:`StepMatcherVisitor.visit`. """

    def test_should_find_step(self):
        """ Scenario: step found """
        # Arrange
        obj = StepMatcherVisitor(sentinel.suite, sentinel.matcher)
        node = Mock()
        # Act
        obj.visit(node)
        # Assert
        node.find_step.assert_called_once_with(sentinel.matcher)

    def test_should_not_find_step(self):
        """ Scenario: step not found """
        # Arrange
        obj = StepMatcherVisitor(sentinel.suite, sentinel.matcher)
        node = Mock()
        exc = MissingStepError('predicate', sentinel.suggest,
                               sentinel.method_name, sentinel.docstring)
        node.find_step.side_effect = [exc]
        # Act
        obj.visit(node)
        # Assert
        node.find_step.assert_called_once_with(sentinel.matcher)
        self.assertTrue(sentinel.docstring in obj._not_matched)

    def test_should_not_find_step_by_method_name_matcher(self):
        """ Scenario: step not found by method name matcher """
        # Arrange
        obj = StepMatcherVisitor(sentinel.suite, sentinel.matcher)
        node = Mock()
        exc = MissingStepError('predicate', sentinel.suggest,
                               sentinel.method_name, '')
        node.find_step.side_effect = [exc]
        # Act
        obj.visit(node)
        # Assert
        node.find_step.assert_called_once_with(sentinel.matcher)
        self.assertTrue(sentinel.method_name in obj._not_matched)


@tags(['unit'])
class StepMatcherVisitorReportMissingTestCase(unittest.TestCase):
    """ Test :py:meth:`StepMatcherVisitor.report_missing`. """

    def test_should_fail_with_suggest(self):
        """ Scenario: fail with suggset """
        # Arrange
        suite = Mock()
        obj = StepMatcherVisitor(suite, sentinel.matcher)
        obj._not_matched = OrderedDict([('docstring', 'suggest string')])
        # Act
        obj.report_missing()
        # Assert
        suite.fail.assert_called_once_with(u'Cannot match steps:\n\nsuggest string')

    def test_should_not_fail(self):
        """ Scenario: no steps missing """
        # Arrange
        suite = Mock()
        obj = StepMatcherVisitor(suite, sentinel.matcher)
        obj._not_matched = OrderedDict()
        # Act
        obj.report_missing()
        # Assert
        self.assertFalse(suite.fail.called)


@tags(['unit'])
class TestVisitorVisitTestCase(unittest.TestCase):
    """ Test :py:meth:`TestVisitor.visit`. """

    def test_should_catch_SystemExit(self):
        """ Scenario: SystemExit """
        # Arrange
        formatter = Mock()
        node = Mock(Step)
        suite = Mock()
        obj = TestVisitor(suite, sentinel.matcher, formatter)
        node.find_step.side_effect = [SystemExit]
        # Act
        # Assert
        self.assertRaises(SystemExit, obj.visit, node)
        formatter.output.assert_called_once_with(node, ANY, 'error', ANY)
