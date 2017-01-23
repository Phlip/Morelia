import os.path
import re
from unittest import TestCase

from morelia.decorators import tags
from morelia.parser import Parser

pwd = os.path.dirname(os.path.realpath(__file__))


class SampleTestCaseMixIn(object):

    def runTest(self):
        pass  # pragma: no cover

    def step_I_have_powered_calculator_on(self):
        r'I have powered calculator on'

        self.stack = []

    def step_I_enter_number_into_the_calculator(self, number):
        r'I enter "([^"]+)" into the calculator'

        self.stack.append(int(number))

    def step_I_press_add(self):
        r'I press add'

        num1 = self.stack.pop()
        num2 = self.stack.pop()
        self.stack.append(num1 + num2)

    def step_the_result_should_be_number_on_the_screen(self, number):
        r'the result should be "([^"]+)" on the screen'

        self.assertEqual(self.stack[-1], int(number))

    def step_I_press_subtract(self):
        r'I press subtract'

        num1 = self.stack.pop()
        num2 = self.stack.pop()
        self.stack.append(num2 - num1)

    def step_I_press_multiply(self):
        r'I press multiply'

        num1 = self.stack.pop()
        num2 = self.stack.pop()
        self.stack.append(num2 * num1)

    def step_I_press_divide(self):
        r'I press divide'

        num1 = self.stack.pop()
        num2 = self.stack.pop()
        self.stack.append(num2 / num1)


@tags(['acceptance'])
class InfoOnAllFailingScenariosTest(TestCase):

    def test_should_report_on_all_failing_scenarios(self):
        self._add_failure_pattern = re.compile('Scenario: Add two numbers\n\s*Then the result should be "120" on the screen\n\s*.*AssertionError:\s*70 != 120', re.DOTALL)
        self._substract_failure_pattern = re.compile('Scenario: Subtract two numbers\n\s*Then the result should be "80" on the screen\n\s*.*AssertionError:\s*70 != 80', re.DOTALL)
        self._multiply_failure_pattern = re.compile('Scenario: Multiply two numbers\n\s*Then the result should be "12" on the screen\n\s*.*AssertionError:\s*3 != 12', re.DOTALL)
        self._division_failure_pattern = re.compile('Scenario: Divide two numbers\n\s*Then the result should be "4" on the screen\n\s*.*AssertionError:\s*2 != 4', re.DOTALL)
        filename = os.path.join(pwd, 'features/info_on_all_failing_scenarios.feature')
        ast = Parser().parse_file(filename)
        ast.evaluate(self)

    def step_feature_with_number_scenarios_has_been_described_in_file(self, feature_file):
        r'that feature with 4 scenarios has been described in file "([^"]+)"'
        filename = os.path.join(pwd, 'features/{}'.format(feature_file))
        self._ast = Parser().parse_file(filename)

    def step_that_test_case_passing_number_and_number_scenario_and_failing_number_and_number_has_been_written(self):
        r'that test case passing 1 and 3 scenario and failing 2 and 4 has been written'

        class _EvaluatedTestCase(SampleTestCaseMixIn, TestCase):

            def step_I_press_subtract(self):
                pass

            def step_I_press_divide(self):
                pass

        self._evaluated_test_case = _EvaluatedTestCase
        self._failing_patterns = [
            self._substract_failure_pattern,
            self._division_failure_pattern
        ]

    def step_that_test_case_failing_all_scenarios_been_written(self):
        r'that test case failing all scenarios been written'

        class _EvaluatedTestCase(SampleTestCaseMixIn, TestCase):

            def step_I_press_add(self):
                pass

            def step_I_press_subtract(self):
                pass

            def step_I_press_multiply(self):
                pass

            def step_I_press_divide(self):
                pass

        self._evaluated_test_case = _EvaluatedTestCase
        self._failing_patterns = [
            self._add_failure_pattern,
            self._substract_failure_pattern,
            self._multiply_failure_pattern,
            self._division_failure_pattern
        ]

    def step_that_test_case_passing_number_number_and_number_scenario_and_failing_number_has_been_written(self):
        r'that test case passing 2, 3 and 4 scenario and failing 1 has been written'

        class _EvaluatedTestCase(SampleTestCaseMixIn, TestCase):

            def step_I_press_add(self):
                pass

        self._evaluated_test_case = _EvaluatedTestCase
        self._failing_patterns = [
            self._add_failure_pattern,
        ]

    def step_that_test_case_passing_all_scenarios_been_written(self):
        r'that test case passing all scenarios been written'

        class _EvaluatedTestCase(SampleTestCaseMixIn, TestCase):
            pass

        self._evaluated_test_case = _EvaluatedTestCase

    def step_that_test_case_failing_number_number_and_number_scenario_and_passing_number_has_been_written(self):
        r'that test case failing 1, 2 and 3 scenario and passing 4 has been written'

        class _EvaluatedTestCase(SampleTestCaseMixIn, TestCase):

            def step_I_press_add(self):
                pass

            def step_I_press_subtract(self):
                pass

            def step_I_press_multiply(self):
                pass

        self._evaluated_test_case = _EvaluatedTestCase
        self._failing_patterns = [
            self._add_failure_pattern,
            self._substract_failure_pattern,
            self._multiply_failure_pattern,
        ]

    def step_I_run_test_case(self):
        r'I run test case'

        self._catch_exception = None
        try:
            tc = self._evaluated_test_case()
            self._ast.evaluate(tc)
        except Exception as e:
            self._catch_exception = e  # warning: possible leak, use with caution

    def step_I_will_get_assertion_error_with_information_number_scenarios_passed_number_scenarios_failed(self, message):
        r'I will get assertion error with information "([^"]+)"'

        message = self._catch_exception.args[0]
        self.assertTrue(message.startswith(message))

    def step_I_will_get_traceback_of_each_failing_scenario(self):
        r'I will get traceback of each failing scenario'

        patterns = self._failing_patterns
        message = self._catch_exception.args[0]
        for pattern in patterns:
            self.assertRegexpMatches(message, pattern)

    def step_I_won_t_get_assertion_error(self):
        r'I won\'t get assertion error'

        self.assertIsNone(self._catch_exception)
