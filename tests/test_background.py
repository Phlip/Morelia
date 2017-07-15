# -*- coding: utf-8 -*-
import os
from unittest import TestCase

from morelia.decorators import tags
from morelia.parser import Parser
from morelia.grammar import Scenario

pwd = os.path.dirname(os.path.realpath(__file__))


@tags(['acceptance'])
class BackgroundTest(TestCase):

    def setUp(self):
        self.__steps_executed = []

    def test_background(self):
        filename = os.path.join(pwd, 'features/background.feature')
        ast = Parser().parse_file(filename)
        self.__scenarios_num = sum(1 for s in ast.steps if isinstance(s, Scenario))
        ast.evaluate(self)

    def step_I_have_some_background_steps_defined(self):
        self.__steps_executed.append('I have some background steps defined')
        try:
            self.__background_step_ran += 1
        except AttributeError:
            self.__background_step_ran = 1

    def step_scenario_is_executed(self):
        self.__steps_executed.append('scenario is executed')

    def step_all_background_steps_are_executed_before_any_step_defined_in_scenario(self):
        background_step = 'I have some background steps defined'
        scenario_step = 'scenario is executed'
        msg = 'Background step not executed before scenario steps'
        self.__assert_background_step_executed_before_scenario_step(background_step, scenario_step, msg)

    def step_other_scenario_is_executed(self):
        self.__steps_executed.append('other scenario is executed')

    def step_background_steps_are_executed_again_before_every_scenario(self):
        background_step = 'I have some background steps defined'
        scenario_step = 'other scenario is executed'
        msg = 'Background step not executed before scenario steps'
        self.__assert_background_step_executed_before_scenario_step(background_step, scenario_step, msg)

    def step_single_scenario_given_step(self):
        self.__steps_executed.append('single scenario given step')

    def step_scenario_given_step_is_executed_after_background_steps(self):
        background_step = 'I have some background steps defined'
        scenario_step = 'single scenario given step'
        msg = 'Background step not executed before scenario given step'
        self.__assert_background_step_executed_before_scenario_step(background_step, scenario_step, msg)

    def __assert_background_step_executed_before_scenario_step(self, background_step, scenario_step, msg):
        background_step_idx = self.__steps_executed.index(background_step)
        scenario_given_step_idx = self.__steps_executed.index(scenario_step)
        self.assertLess(background_step_idx, scenario_given_step_idx, msg=msg)

    def step_step_contains_angle_variable(self, angle_variable):
        r'step contains (.+)'
        self.__angle_variable = angle_variable

    def step_background_step_with_angle_variable_will_be_executed(self, angle_variable):
        r'background step with (.+) will be executed'
        self.assertEqual(angle_variable, self.__angle_variable)

    def step_all_scenarios_are_executed(self):
        pass

    def step_background_steps_will_be_executed_once_per_every_scenario_case(self):
        self.assertLessEqual(self.__scenarios_num, self.__background_step_ran, msg='Background step not executed for every scenario')
        self.assertGreaterEqual(self.__scenarios_num, self.__background_step_ran, msg='Background step executed more then once for every scenario')
