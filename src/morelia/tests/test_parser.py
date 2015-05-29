from unittest import TestCase

from morelia.decorators import tags
from morelia.exceptions import WrongNodeTaggedError
from morelia.grammar import Feature, Step
from morelia.parser import LabelParser, LanguageParser


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


@tags(['unit'])
class LanguageParserParseTestCase(TestCase):
    """ Test :py:meth:`LanguageParser.parse`. """

    def test_should_return_false_if_line_without_language_directive(self):
        """ Scenario: line without language directive """
        # Arrange
        obj = LanguageParser()
        lines = [
            '# language: ',  # missing language
            'Feature:',  # not a language directive
            'language: pl',  # missing comment
            '# comment',  # comment
        ]
        for line in lines:
            # Act
            result = obj.parse(line)
            # Assert
            self.assertFalse(result)
            self.assertEqual(obj.get_language(), 'en')

    def test_should_return_true_if_line_with_language_directive(self):
        """ Scenario: line with language directive """
        # Arrange
        obj = LanguageParser()
        line = '# language: pl'
        # Act
        result = obj.parse(line)
        # Assert
        self.assertTrue(result)
        self.assertEqual(obj.get_language(), 'pl')
