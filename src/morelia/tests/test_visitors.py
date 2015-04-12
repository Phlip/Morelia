import unittest
from collections import OrderedDict
from mock import Mock, sentinel

from morelia.exceptions import MissingStepError
from morelia.visitors import StepMatcherVisitor


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
        suggest = 'suggest'
        node.find_step.side_effect = [MissingStepError('predicate', suggest)]
        # Act
        obj.visit(node)
        # Assert
        node.find_step.assert_called_once_with(sentinel.suite, sentinel.matcher)
        self.assertTrue(suggest in obj._not_matched)


class StepMatcherVisitorAfterFeatureTestCase(unittest.TestCase):
    """ Test :py:meth:`StepMatcherVisitor.after_feature`. """

    def test_should_fail_with_suggest(self):
        """ Scenario: fail with suggset """
        # Arrange
        suite = Mock()
        obj = StepMatcherVisitor(suite, sentinel.matcher)
        obj._not_matched = OrderedDict([('suggest string', True)])
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
