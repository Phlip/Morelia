# -*- coding: utf-8 -*-
import os
from unittest import TestCase

from morelia import run
from morelia.decorators import tags

pwd = os.path.dirname(os.path.realpath(__file__))


@tags(['acceptance'])
class DocStringTest(TestCase):

    def test_docstrings_should_be_passed_as_text_to_step(self):
        filename = os.path.join(pwd, 'features/docstrings.feature')
        run(filename, self)

    def step_I_have_step_with_docstring(self, _text=None):
        r'I have step with docstring'

        self.assertIsNotNone(_text)
        self._text = _text

    def step_above_step_is_executed(self):
        r'above step is executed'

    def step_it_has_docstring_passed_in_text_variable(self):
        r'it has docstring passed in _text variable'

        self.assertEqual(self._text, 'Docstring line1\nline2')
