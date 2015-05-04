import unittest
from collections import OrderedDict
from mock import Mock, sentinel, ANY

from morelia.exceptions import MissingStepError
from morelia.visitors import StepMatcherVisitor, TestVisitor


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
        node.find_step.assert_called_once_with(sentinel.suite, sentinel.matcher)

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
        node.find_step.assert_called_once_with(sentinel.suite, sentinel.matcher)
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
        node.find_step.assert_called_once_with(sentinel.suite, sentinel.matcher)
        self.assertTrue(sentinel.method_name in obj._not_matched)


class StepMatcherVisitorAfterFeatureTestCase(unittest.TestCase):
    """ Test :py:meth:`StepMatcherVisitor.after_feature`. """

    def test_should_fail_with_suggest(self):
        """ Scenario: fail with suggset """
        # Arrange
        suite = Mock()
        obj = StepMatcherVisitor(suite, sentinel.matcher)
        obj._not_matched = OrderedDict([('docstring', 'suggest string')])
        # Act
        obj.after_feature(sentinel.node)
        # Assert
        suite.fail.assert_called_once_with(u'Cannot match steps:\n\nsuggest string')

    def test_should_not_fail(self):
        """ Scenario: no steps missing """
        # Arrange
        suite = Mock()
        obj = StepMatcherVisitor(suite, sentinel.matcher)
        obj._not_matched = OrderedDict()
        # Act
        obj.after_feature(sentinel.node)
        # Assert
        self.assertFalse(suite.fail.called)


class TestVisitorVisitTestCase(unittest.TestCase):
    """ Test :py:meth:`TestVisitor.visit`. """

    def test_should_catch_SystemExit(self):
        """ Scenario: SystemExit """
        # Arrange
        formatter = Mock()
        node = Mock()
        obj = TestVisitor(sentinel.suite, sentinel.matcher, formatter)
        node.test_step.side_effect = [SystemExit]
        # Act
        # Assert
        self.assertRaises(SystemExit, obj.visit, node)
        formatter.output.assert_called_once_with(node, ANY, 'error', ANY)
