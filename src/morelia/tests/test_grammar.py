import unittest

from mock import sentinel, Mock, ANY

from morelia.grammar import AST


class ASTEvaluateTestCase(unittest.TestCase):
    """ Test :py:meth:`AST.evaluate`. """

    def test_should_use_provided_matcher(self):
        """ Scenariusz: matcher given as parameter """
        # Arrange
        test_visitor_class = Mock()
        matcher_class = Mock()
        feature = Mock()
        steps = [feature]
        obj = AST(steps, test_visitor_class=test_visitor_class)
        # Act
        obj.evaluate(sentinel.suite, matchers=[matcher_class])
        # Assert
        test_visitor_class.assert_called_once_with(sentinel.suite, matcher_class.return_value, ANY)

    def test_should_use_provided_formatter(self):
        """ Scenariusz: formatter given as parameter """
        # Arrange
        test_visitor = Mock()
        formatter = Mock()
        feature = Mock()
        steps = [feature]
        obj = AST(steps, test_visitor_class=test_visitor)
        # Act
        obj.evaluate(sentinel.suite, formatter=formatter)
        # Assert
        test_visitor.assert_called_once_with(sentinel.suite, ANY, formatter)

    def test_should_show_all_missing_steps(self):
        """ Scenariusz: show all missing steps """
        # Arrange
        matcher_visitor = Mock()
        feature = Mock()
        steps = [feature]
        obj = AST(steps, matcher_visitor_class=matcher_visitor)
        # Act
        obj.evaluate(sentinel.suite, show_all_missing=True)
        # Assert
        matcher_visitor.assert_called_once_with(sentinel.suite, ANY)
