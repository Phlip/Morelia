from six.moves import StringIO
import unittest

from mock import sentinel, Mock

from morelia.formatters import NullFormatter, PlainTextFormatter, ColorTextFormatter


class NullFormatterOutputTestCase(unittest.TestCase):
    """ Test :py:meth:`NullFormatter.output`. """

    def test_should_do_nothing(self):
        """ Scenario: do nothing """
        # Arrange
        obj = NullFormatter()
        # Act
        line = 'Given some number'
        status = 'pass'
        duration = 0.01
        obj.output(sentinel.node, line, status, duration)


class PlainTextFormatterOutputTestCase(unittest.TestCase):
    """ Test :py:meth:`PlainTextFormatter.output`. """

    def test_should_output_for_pass(self):
        """ Scenariusz: format for pass """
        # Arrange
        stream = StringIO()
        obj = PlainTextFormatter(stream)
        # Act
        line = 'Given some number'
        status = 'pass'
        duration = 0.01
        node = Mock()
        node.is_executable.return_value = True
        obj.output(node, line, status, duration)
        # Assert
        expected = '%-60s # pass  0.010s\n' % line
        self.assertEqual(stream.getvalue(), expected)

    def test_should_output_for_fail(self):
        """ Scenariusz: format for fail """
        # Arrange
        stream = StringIO()
        obj = PlainTextFormatter(stream)
        # Act
        line = 'Given some number'
        status = 'fail'
        duration = 0.01
        node = Mock()
        node.is_executable.return_value = True
        obj.output(node, line, status, duration)
        # Assert
        expected = '%-60s # fail  0.010s\n' % line
        self.assertEqual(stream.getvalue(), expected)

    def test_should_output_for_error(self):
        """ Scenariusz: format for error """
        # Arrange
        stream = StringIO()
        obj = PlainTextFormatter(stream)
        # Act
        line = 'Given some number'
        status = 'error'
        duration = 0.01
        node = Mock()
        node.is_executable.return_value = True
        obj.output(node, line, status, duration)
        # Assert
        expected = '%-60s # error 0.010s\n' % line
        self.assertEqual(stream.getvalue(), expected)

    def test_should_output_for_not_step(self):
        """ Scenariusz: format for not a step """
        # Arrange
        stream = StringIO()
        obj = PlainTextFormatter(stream)
        # Act
        line = 'Scenario: some number'
        status = 'pass'
        duration = 0.01
        node = Mock()
        node.is_executable.return_value = False
        obj.output(node, line, status, duration)
        # Assert
        expected = '%s\n' % line
        self.assertEqual(stream.getvalue(), expected)


class ColorTextFormatterOutputTestCase(unittest.TestCase):
    """ Test :py:meth:`ColorTextFormatter.output`. """

    def test_should_output_for_pass(self):
        """ Scenariusz: format for pass """
        # Arrange
        stream = StringIO()
        obj = ColorTextFormatter(stream)
        # Act
        line = 'Given some number'
        status = 'pass'
        duration = 0.01
        node = Mock()
        node.is_executable.return_value = True
        obj.output(node, line, status, duration)
        # Assert
        green = u'\x1b[32m'
        reset = u'\x1b[0m'
        expected = '%s%-60s # 0.010s%s\n' % (green, line, reset)
        self.assertEqual(stream.getvalue(), expected)

    def test_should_output_for_fail(self):
        """ Scenariusz: format for fail """
        # Arrange
        stream = StringIO()
        obj = ColorTextFormatter(stream)
        # Act
        line = 'Given some number'
        status = 'fail'
        duration = 0.01
        node = Mock()
        node.is_executable.return_value = True
        obj.output(node, line, status, duration)
        # Assert
        red = u'\x1b[31m'
        reset = u'\x1b[0m'
        expected = '%s%-60s # 0.010s%s\n' % (red, line, reset)
        self.assertEqual(stream.getvalue(), expected)

    def test_should_output_for_error(self):
        """ Scenariusz: format for error """
        # Arrange
        stream = StringIO()
        obj = ColorTextFormatter(stream)
        # Act
        line = 'Given some number'
        status = 'error'
        duration = 0.01
        node = Mock()
        node.is_executable.return_value = True
        obj.output(node, line, status, duration)
        # Assert
        red = u'\x1b[31m'
        reset = u'\x1b[0m'
        expected = '%s%-60s # 0.010s%s\n' % (red, line, reset)
        self.assertEqual(stream.getvalue(), expected)

    def test_should_output_for_not_step(self):
        """ Scenariusz: format for not a step """
        # Arrange
        stream = StringIO()
        obj = ColorTextFormatter(stream)
        # Act
        line = 'Scenario: some number'
        status = 'pass'
        duration = 0.01
        node = Mock()
        node.is_executable.return_value = False
        obj.output(node, line, status, duration)
        # Assert
        expected = '%s\n' % line
        self.assertEqual(stream.getvalue(), expected)
