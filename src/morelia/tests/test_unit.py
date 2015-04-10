#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase

from mock import sentinel, patch, Mock

from morelia.base import Parser, DEFAULT_LANGUAGE, Morelia, MissingStepError, Step


class ParserParseLanguageDirectiveTestCase(TestCase):
    """ Test :py:meth:`Parser.parse_language_directive`. """

    def test_should_return_true_on_language_directive_line(self):
        """ Scenario: line with language directive """
        # Arrange
        obj = Parser()
        for lang in ['en', 'pl', 'ja']:
            line = '# language: %s' % lang
            # Act
            result = obj.parse_language_directive(line)
            # Assert
            self.assertTrue(result)
            self.assertEqual(obj.language, lang)

    def test_should_return_false_if_no_language_directive(self):
        """ Scenario: line without language directive """
        # Arrange
        obj = Parser()
        lines = [
            '# language: ',  # missing language
            'Feature:',  # not a language directive
            'language: pl',  # missing comment
            '# comment',  # comment
        ]
        for line in lines:
            # Act
            result = obj.parse_language_directive(line)
            # Assert
            self.assertFalse(result)
            self.assertEqual(obj.language, DEFAULT_LANGUAGE)


class MoreliaReconstructionTestCase(TestCase):
    """ Test :py:meth:`Morelia.reconstruction`. """

    def test_should_reconstruct_unicode(self):
        """ Scenario: unicode input """
        # Arrange
        obj = Morelia()
        obj.concept = '???'
        obj.predicate = u'zażółć gęślą jaźń'
        # Act
        result = obj.reconstruction()
        # Assert
        self.assertEqual(result, u'???: zażółć gęślą jaźń\n')

    def test_should_reconstruct_utf8(self):
        """ Scenario: utf8 input """
        # Arrange
        obj = Morelia()
        obj.concept = '???'
        obj.predicate = 'zażółć gęślą jaźń'
        # Act
        result = obj.reconstruction()
        # Assert
        self.assertEqual(result, u'???: zażółć gęślą jaźń\n')


class MissingStepErrorTestCase(TestCase):
    """ Test :py:meth:`MissingStepError`. """

    def test_should_create_exception(self):
        """ Scenario: exception with step and suggest """
        # Arrange
        # Act
        result = MissingStepError('predicate line', 'def step_predicate_line(self):\n    pass')
        # Assert
        self.assertTrue(result is not None)
        self.assertEqual(result.predicate, 'predicate line')


class StepFindStepTestCase(TestCase):
    """ Test :py:meth:`Step.find_step`. """

    def test_should_find_method_name_by_doc_string(self):
        """ Scenario: found by docstring """
        # Arrange
        obj = Step()
        obj.predicate = 'method'
        # Act
        with patch.object(Step, '_find_by_doc_string') as find_by_doc_string:
            find_by_doc_string.return_value = sentinel.method, []
            result, matches = obj.find_step(sentinel.suite)
        # Assert
        self.assertEqual(result, sentinel.method)

    def test_should_find_method_by_name(self):
        """ Scenario: found by name """
        # Arrange
        obj = Step()
        obj.predicate = 'method'
        # Act
        with patch.object(Step, '_find_by_doc_string') as find_by_doc_string:
            with patch.object(Step, '_find_by_name') as find_by_name:
                find_by_doc_string.return_value = None, []
                find_by_name.return_value = sentinel.method, []
                result, matches = obj.find_step(sentinel.suite)
        # Assert
        self.assertEqual(result, sentinel.method)

    def test_should_not_find_method(self):
        """ Scenario: not found """
        # Arrange
        obj = Step()
        obj.predicate = u'some_method'
        with patch.object(Step, '_find_by_doc_string') as find_by_doc_string:
            with patch.object(Step, '_find_by_name') as find_by_name:
                find_by_doc_string.return_value = None, []
                find_by_name.return_value = None, []
                self.assertRaises(MissingStepError, obj.find_step, sentinel.suite)


class StepFindByDocStringTestCase(TestCase):
    """ Test :py:meth:`Step._find_by_doc_string`. """

    def test_should_find_by_doc_string(self):
        """ Scenario: found by doc string """
        # Arrange
        obj = Step()
        methods = {}
        for i in range(10):
            name = 'step_method%s' % i
            method = Mock(__doc__='method%s' % i)
            methods[name] = method
        step_methods = methods.keys()
        suite = Mock(**methods)
        # Act
        result, matches = obj._find_by_doc_string(suite, step_methods, 'method1')
        # Assert
        self.assertEqual(result, methods['step_method1'])

    def test_should_not_find_if_no_match(self):
        """ Scenario: no match """
        # Arrange
        obj = Step()
        methods = {}
        for i in range(10):
            name = 'step_method%s' % i
            method = Mock(__doc__='method%s' % i)
            methods[name] = method
        step_methods = methods.keys()
        suite = Mock(**methods)
        # Act
        result, matches = obj._find_by_doc_string(suite, step_methods, 'no_match')
        # Assert
        self.assertTrue(result is None)

    def test_should_not_find_if_no_docstring(self):
        """ Scenario: no docstring """
        # Arrange
        obj = Step()
        methods = {}
        for i in range(10):
            name = 'step_method%s' % i
            method = Mock()
            methods[name] = method
        step_methods = methods.keys()
        suite = Mock(**methods)
        # Act
        result, matches = obj._find_by_doc_string(suite, step_methods, 'no_match')
        # Assert
        self.assertTrue(result is None)


class StepFindByNameTestCase(TestCase):
    """ Test :py:meth:`Step._find_by_name`. """

    def test_should_find_by_name(self):
        """ Scenario: found by name """
        # Arrange
        obj = Step()
        obj.predicate = 'method1'
        methods = {}
        for i in range(10):
            name = 'step_method%s' % i
            method = Mock(__doc__='method%s' % i)
            methods[name] = method
        step_methods = methods.keys()
        suite = Mock(**methods)
        # Act
        result, matches = obj._find_by_name(suite, step_methods, obj.predicate)
        # Assert
        self.assertEqual(result, methods['step_method1'])
        self.assertEqual(matches, [])

    def test_should_not_find_by_name(self):
        """ Scenario: not found by name """
        # Arrange
        obj = Step()
        obj.predicate = 'no_match'
        methods = {}
        for i in range(10):
            name = 'step_method%s' % i
            method = Mock(__doc__='method%s' % i)
            methods[name] = method
        step_methods = methods.keys()
        suite = Mock(**methods)
        # Act
        result, matches = obj._find_by_name(suite, step_methods, obj.predicate)
        # Assert
        self.assertTrue(result is None)
        self.assertEqual(matches, [])
