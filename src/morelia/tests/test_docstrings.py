# -*- coding: utf-8 -*-
import os
from unittest import TestCase

from morelia.decorators import tags
from morelia.parser import Parser

pwd = os.path.dirname(os.path.realpath(__file__))


@tags(['acceptance'])
class DocStringTest(TestCase):

    def test_docstrings_should_be_passed_as_text_to_step(self):
        filename = os.path.join(pwd, 'features/docstrings.feature')
        ast = Parser().parse_file(filename)
        ast.evaluate(self, show_all_missing=True)

    def step_with_docstring(self, _text=None):
        r'step with docstring'

        self.assertIsNotNone(_text)
        self._text = _text

    def step_step_without_docstring(self):
        r'step without docstring'

        self.assertEqual(self._text, 'Docstring line1\nline2')
