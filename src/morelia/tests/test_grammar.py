from unittest import TestCase

from mock import sentinel, Mock, ANY

from morelia.decorators import tags
from morelia.grammar import AST, Feature, Morelia, Step

from morelia.visitors import IVisitor
from morelia.matchers import IStepMatcher
from morelia.formatters import IFormatter


@tags(['unit'])
class ASTEvaluateTestCase(TestCase):
    """ Test :py:meth:`AST.evaluate`. """

    def test_should_use_provided_matcher(self):
        """ Scenariusz: matcher given as parameter """
        # Arrange
        test_visitor_class = Mock(IVisitor)
        matcher_class = Mock(IStepMatcher)
        feature = Mock(Feature)
        steps = [feature]
        obj = AST(steps, test_visitor_class=test_visitor_class)
        # Act
        obj.evaluate(sentinel.suite, matchers=[matcher_class])
        # Assert
        test_visitor_class.assert_called_once_with(sentinel.suite, matcher_class.return_value, ANY)

    def test_should_use_provided_formatter(self):
        """ Scenariusz: formatter given as parameter """
        # Arrange
        test_visitor = Mock(IVisitor)
        formatter = Mock(IFormatter)
        feature = Mock(Feature)
        steps = [feature]
        obj = AST(steps, test_visitor_class=test_visitor)
        # Act
        obj.evaluate(sentinel.suite, formatter=formatter)
        # Assert
        test_visitor.assert_called_once_with(sentinel.suite, ANY, formatter)

    def test_should_show_all_missing_steps(self):
        """ Scenariusz: show all missing steps """
        # Arrange
        matcher_visitor = Mock(IVisitor)
        feature = Mock(Feature)
        steps = [feature]
        obj = AST(steps, matcher_visitor_class=matcher_visitor)
        suite = Mock()
        # Act
        obj.evaluate(suite, show_all_missing=True)
        # Assert
        matcher_visitor.assert_called_once_with(suite, ANY)


@tags(['unit'])
class LabeledNodeGetLabelsTestCase(TestCase):

    def test_should_return_node_labels(self):
        """ Scenario: node labels """
        # Arrange
        expected = ['label1', 'label2']
        obj = Feature(None, None)
        obj.add_labels(expected)
        # Act
        result = obj.get_labels()
        # Assert
        self.assertEqual(result, expected)

    def test_should_return_node_and_parent_labels(self):
        """ Scenario: node and parent labels """
        # Arrange
        expected = ['label1', 'label2']
        obj = Feature(None, None)
        obj.add_labels(['label1'])
        parent = Feature(None, None)
        parent.add_labels(['label2'])
        obj.parent = parent
        # Act
        result = obj.get_labels()
        # Assert
        self.assertEqual(result, expected)


@tags(['unit'])
class INodeEvaluateStepsTest(TestCase):

    node_class = Morelia

    def test_should_call_visitor(self):
        # Arrange
        node = self.node_class('Feature', 'Some feature')
        visitor = Mock(IVisitor)
        # Act
        node.evaluate_steps(visitor)
        # Assert
        visitor.visit.assert_called_once_with(node)

    def test_should_evaluate_child_steps(self):
        # Arrange
        steps = [Mock(Step), Mock(Step)]
        node = self.node_class('Feature', 'Some feature', steps=steps)
        visitor = Mock(IVisitor)
        # Act
        node.evaluate_steps(visitor)
        # Assert
        visitor.visit.assert_called_once_with(node)
        for step in steps:
            step.evaluate_steps.assert_called_once_with(visitor)


@tags(['unit'])
class FeatureEvaluateChildStepsTest(INodeEvaluateStepsTest):

    node_class = Feature

    def test_should_raise_assertion_error_if_first_scenario_fail(self):
        # Arrange
        steps = []
        for i in range(2):
            step = Mock(Step)
            if i == 0:
                step.evaluate_steps.side_effect = AssertionError('{} scenario failure'.format(i))
            steps.append(step)
        node = self.node_class('Feature', 'Some feature', steps=steps)
        visitor = Mock(IVisitor)
        # Act
        try:
            node.evaluate_steps(visitor)
        except AssertionError as exc:
            self.assertIn('1 scenario failed, 1 scenario passed', exc.args[0])
        else:
            self.fail('AssertionError not raised')
        # Assert
        visitor.visit.assert_called_once_with(node)
        for step in steps:
            step.evaluate_steps.assert_called_once_with(visitor)

    def test_should_raise_assertion_error_if_second_scenario_fail(self):
        # Arrange
        steps = []
        for i in range(3):
            step = Mock(Step)
            if i == 1:
                step.evaluate_steps.side_effect = AssertionError('{} scenario failure'.format(i))
            steps.append(step)
        node = self.node_class('Feature', 'Some feature', steps=steps)
        visitor = Mock(IVisitor)
        # Act
        try:
            node.evaluate_steps(visitor)
        except AssertionError as exc:
            self.assertIn('1 scenario failed, 2 scenarios passed', exc.args[0])
        else:
            self.fail('AssertionError not raised')
        # Assert
        visitor.visit.assert_called_once_with(node)
        for step in steps:
            step.evaluate_steps.assert_called_once_with(visitor)

    def test_should_raise_assertion_error_with_tracebacks_from_all_exceptions(self):
        # Arrange
        steps = []
        for i in range(4):
            step = Mock(Step)
            if i in (1, 2):
                step.evaluate_steps.side_effect = AssertionError('{} scenario failure'.format(i))
            step.reconstruction.return_value = '\nStep'
            steps.append(step)
        node = self.node_class('Feature', 'Some feature', steps=steps)
        visitor = Mock(IVisitor)
        # Act
        try:
            node.evaluate_steps(visitor)
        except AssertionError as exc:
            message = exc.args[0]
            self.assertIn('2 scenarios failed, 2 scenarios passed', message)
            self.assertIn('AssertionError: 1 scenario failure', message)
            self.assertIn('AssertionError: 2 scenario failure', message)
            self.assertIn('in _evaluate_child_steps', message)
        else:
            self.fail('AssertionError not raised')
        # Assert
        visitor.visit.assert_called_once_with(node)
        for step in steps:
            step.evaluate_steps.assert_called_once_with(visitor)
