# -*- coding: utf-8 -*-
import os
from unittest import TestCase

from morelia import run
from morelia.decorators import tags

pwd = os.path.dirname(os.path.realpath(__file__))


@tags(['acceptance'])
class LabelTest(TestCase):

    def setUp(self):
        self.__labels = []

    def test_labels(self):
        filename = os.path.join(pwd, 'features/labels.feature')
        run(filename, self)

    def step_step_which_accepts__labels_variable_is_executed(self, _labels=None):
        self.__labels = _labels

    def step_it_will_get_labels(self, labels):
        r'it will get labels "([^"]+)"'

        expected = labels.split(',')
        self.assertEqual(set(expected), set(self.__labels))

    def step_step_which_does_not_accepts__labels_variable_is_executed(self):
        pass

    def step_it_will_not_get_any_labels(self):
        self.assertEqual(0, len(self.__labels))
