# -*- coding: utf-8 -*-
import os
from unittest import TestCase

from morelia import run
from morelia.decorators import tags

pwd = os.path.dirname(os.path.realpath(__file__))


@tags(['acceptance'])
class DocStringTest(TestCase):

    def test_docstrings(self):
        filename = os.path.join(pwd, 'features/docstrings.feature')
        run(filename, self)

    def step_I_put_docstring_after_step_definition(self, _text=None):
        self.assertIsNotNone(_text)
        self._text = _text

    def step_I_will_get_docstring_passed_in__text_variable(self):
        r'I will get docstring passed in _text variable'
        self.assertEqual(self._text, 'Docstring line1\nline2')
