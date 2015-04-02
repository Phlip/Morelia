#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase


from morelia.base import Parser, DEFAULT_LANGUAGE, Morelia


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
        """ Scenariusz: unicode input """
        # Arrange
        obj = Morelia()
        obj.concept = '???'
        obj.predicate = u'zażółć gęślą jaźń'
        # Act
        result = obj.reconstruction()
        # Assert
        self.assertEqual(result, u'???: zażółć gęślą jaźń\n')

    def test_should_reconstruct_utf8(self):
        """ Scenariusz: utf8 input """
        # Arrange
        obj = Morelia()
        obj.concept = '???'
        obj.predicate = 'zażółć gęślą jaźń'
        # Act
        result = obj.reconstruction()
        # Assert
        self.assertEqual(result, u'???: zażółć gęślą jaźń\n')
