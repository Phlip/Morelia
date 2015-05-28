from unittest import TestCase

from morelia.decorators import tags
from morelia.exceptions import WrongNodeTaggedError
from morelia.grammar import Feature, Step
from morelia.parser import LabelParser


@tags(['unit'])
class LabelParserParseTestCase(TestCase):
    """ Test :py:meth:`LabelParser.parse`. """

    def test_should_return_false_if_line_without_labels(self):
        """ Scenario: line without labels """
        # Arrange
        obj = LabelParser()
        line = ''
        # Act
        result = obj.parse(line)
        # Assert
        self.assertFalse(result)

    def test_should_return_true_if_line_with_labels(self):
        """ Scenario: line with labels """
        # Arrange
        obj = LabelParser()
        line = '@label1'
        # Act
        result = obj.parse(line)
        # Assert
        self.assertTrue(result)


@tags(['unit'])
class LabelParserAppendToTestCase(TestCase):
    """ Test :py:meth:`LabelParser.append_to`. """

    def test_should_not_append_if_no_labels(self):
        """ Scenario: no labels """
        # Arrange
        obj = LabelParser()
        node = Feature(None, None)
        # Act
        obj.append_to(node)
        # Assert
        self.assertEqual(node._labels, [])

    def test_should_append_to_feature_or_scenario(self):
        """ Scenario: append to feature and scenario """
        # Arrange
        obj = LabelParser()
        obj.parse('@label1')
        node = Feature(None, None)
        # Act
        obj.append_to(node)
        # Assert
        self.assertEqual(node._labels, ['label1'])
        self.assertEqual(obj._labels, [])

    def test_should_raise_exception_if_not_feature_or_scenario(self):
        """ Scenario: not a feature or scenario """
        # Arrange
        obj = LabelParser()
        obj.parse('@label1')
        node = Step(None, None)
        # Act
        # Assert
        self.assertRaises(WrongNodeTaggedError, obj.append_to, node)
