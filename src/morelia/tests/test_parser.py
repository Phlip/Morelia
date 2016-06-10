from unittest import TestCase

from morelia.decorators import tags
from morelia.parser import LabelParser, LanguageParser, LineSource, DocStringParser


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
class LabelParserPopLabelsTestCase(TestCase):
    """ Test :py:meth:`LabelParser.pop_labels`. """

    def test_should_not_return_labels(self):
        """ Scenario: no labels """
        # Arrange
        obj = LabelParser()
        # Act
        result = obj.pop_labels()
        # Assert
        self.assertEqual(result, [])

    def test_should_return_labels(self):
        """ Scenario: pop labels """
        # Arrange
        obj = LabelParser()
        obj.parse('@label1')
        # Act
        result = obj.pop_labels()
        # Assert
        self.assertEqual(result, ['label1'])
        self.assertEqual(obj._labels, [])

    def test_should_not_return_labels_when_tag_inside_step(self):
        """ Scenario: no labels when tag inside step"""
        # Arrange
        obj = LabelParser()
        obj.parse('When abc@example.com')
        # Act
        result = obj.pop_labels()
        # Assert
        self.assertEqual(result, [])
        self.assertEqual(obj._labels, [])


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
            self.assertEqual(obj.language, 'en')

    def test_should_return_true_if_line_with_language_directive(self):
        """ Scenario: line with language directive """
        # Arrange
        obj = LanguageParser()
        line = '# language: pl'
        # Act
        result = obj.parse(line)
        # Assert
        self.assertTrue(result)
        self.assertEqual(obj.language, 'pl')

    def test_should_set_default_language(self):
        """ Scenario: default language passed """
        # Arrange
        obj = LanguageParser(default_language='ja')
        line = ''
        # Act
        result = obj.parse(line)
        # Assert
        self.assertFalse(result)
        self.assertEqual(obj.language, 'ja')


@tags(['unit'])
class LineProducerGetLineTestCase(TestCase):
    """ Test :py:meth:`LineProducer.get_line`. """

    def test_should_raise_stop_iteration_if_no_text(self):
        """ Scenario: no text """
        # Arrange
        obj = LineSource('')
        # Act
        # Assert
        self.assertRaises(StopIteration, obj.get_line)

    def test_should_return_line_by_line(self):
        """ Scenario: return lines """
        # Arrange
        lines = 'line1\nline2\nline3'
        obj = LineSource(lines)
        # Act
        for i, line in enumerate(lines.split('\n')):
            result = obj.get_line()
            # Assert
            self.assertEqual(result, line)
            self.assertEqual(obj.line_number, i + 1)


class DocStringParserParseTestCase(TestCase):
    """ Test :py:meth:`DocStringParser.parse`. """

    def test_should_return_false_if_not_docstring_beginning(self):
        """ Scenario: not a docstring """
        # Arrange
        obj = DocStringParser(None)
        lines = [
            '',
            'Feature: feature',
            '# comment',
            '"',
        ]
        for line in lines:
            # Act
            result = obj.parse(line)
            # Assert
            self.assertFalse(result)

    def test_should_return_true_if_docstring(self):
        """ Scenario: docstring """
        # Arrange
        lines = '"""\nline1\nline2\n"""'
        line_source = LineSource(lines)
        obj = DocStringParser(line_source)
        line = line_source.get_line()
        # Act
        result = obj.parse(line)
        # Assert
        self.assertTrue(result)
        self.assertEqual(obj.payload, 'line1\nline2')

    def test_should_return_true_if_indented_docstring(self):
        """ Scenario: indented docstring """
        # Arrange
        test_data = [
            ('   """\n   line1\n   line2\n   """', 'line1\nline2'),
            ('   """\n     line1\n   line2\n   """', '  line1\nline2'),
        ]
        for lines, expected in test_data:
            line_source = LineSource(lines)
            obj = DocStringParser(line_source)
            line = line_source.get_line()
            # Act
            result = obj.parse(line)
            # Assert
            self.assertTrue(result)
            self.assertEqual(obj.payload, expected)
