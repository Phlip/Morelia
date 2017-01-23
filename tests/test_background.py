# -*- coding: utf-8 -*-
import os
from unittest import TestCase

from morelia.decorators import tags
from morelia.parser import Parser
from morelia.grammar import Scenario

pwd = os.path.dirname(os.path.realpath(__file__))


@tags(['acceptance'])
class BackgroundTest(TestCase):

    def test_background(self):
        filename = os.path.join(pwd, 'features/background.feature')
        ast = Parser().parse_file(filename)
        self._scenarios_num = sum(1 for s in ast.steps if isinstance(s, Scenario))
        ast.evaluate(self)

    def step_step_ran_is_number(self, number):
        r'step_ran was "([^"]+)"'

        self._step_ran = int(number)

    def step_alt_step_ran_is_number(self, number):
        r'alt_step_ran was "([^"]+)"'

        self._alt_step_ran = int(number)

    def step_I_increment_step_ran_by_number(self, number):
        r'I increment step_ran by "([^"]+)"'

        self._step_ran += int(number)

    def step_increment_alt_step_ran_by_number(self, number):
        r'increment alt_step_ran by "([^"]+)"'

        self._alt_step_ran += int(number)

    def step_step_ran_equals_number(self, number):
        r'step_ran will equal "([^"]+)"'

        self.assertEqual(self._step_ran, int(number))

    def step_alt_step_ran_equals_number(self, number):
        r'alt_step_ran will equal "([^"]+)"'

        self.assertEqual(self._alt_step_ran, int(number))

    def step_angles_step_is_background(self, background):
        r'angles_step was (.+)'

        self._background = background

    def step_I_increment_angles_step_by_when(self, when):
        r'I increment angles_step by (.+)'

        self._background = int(self._background) + int(when)

    def step_angles_step_equals_then(self, then):
        r'angles_step will equal (.+)'

        self.assertEqual(self._background, int(then))

    def step_angles_step_will_be_then(self, then):
        r'angles_step will be string "([^"]+)"'

        self.assertEqual(self._background, then)

    def step_background_only_step_ran_incremented(self):
        r'background_only_step_ran incremented'

        try:
            self._background_only_step_ran += 1
        except AttributeError:
            self._background_only_step_ran = 1

    def step_background_only_step_ran_will_equal_scenarios_number(self):
        r'background_only_step_ran will equal scenarios number'

        self.assertEqual(self._background_only_step_ran, self._scenarios_num)
