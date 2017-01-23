# -*- coding: utf-8 -*-
import os
from unittest import TestCase

from morelia.decorators import tags
from morelia.parser import Parser

pwd = os.path.dirname(os.path.realpath(__file__))


@tags(['acceptance'])
class LabelTest(TestCase):

    def test_labels(self):
        filename = os.path.join(pwd, 'features/labels.feature')
        ast = Parser().parse_file(filename)
        ast.evaluate(self, show_all_missing=True)

    def step_with_labels(self, _labels=None):
        r'step with _labels'

        self.assertIsNotNone(_labels)
        self.assertEqual(set(['label1', 'label2']), set(_labels))

    def step_with_kwargs(self, **kwargs):
        r'step with kwargs'

        _labels = kwargs['_labels']
        self.assertIsNotNone(_labels)

    def step_without_labels(self):
        r'step without _labels'
        pass

    def step_I_should_get_labels(self, labels, _labels):
        r'I should get labels "([^"]+)"'

        expected = ['label{}'.format(label) for label in labels.split(',')]
        self.assertEqual(set(expected), set(_labels))

    def step_step_with_label(self, label, _labels):
        r'step with "([^"]+)"'

        self.assertFalse(label in set(_labels))
