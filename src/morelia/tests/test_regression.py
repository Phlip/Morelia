import os
from unittest import TestCase

from morelia.decorators import tags
from morelia.parser import Parser

pwd = os.path.dirname(os.path.realpath(__file__))


@tags(['acceptance', 'regression'])
class SetUpTearDownTest(TestCase):

    def setUp(self):
        try:
            self._setup_count += 1
        except AttributeError:
            self._setup_count = 1

    def tearDown(self):
        try:
            self._teardown_count += 1
        except AttributeError:
            self._teardown_count = 1

    def test_setup_teardown(self):
        filename = pwd + '/features/setupteardown.feature'
        ast = Parser().parse_file(filename)
        ast.evaluate(self, show_all_missing=True)

    def test_many_test_methods(self):
        filename = pwd + '/features/setupteardown.feature'
        ast = Parser().parse_file(filename)
        ast.evaluate(self, show_all_missing=True)

    def test_not_morelia_test(self):
        setup_count = getattr(self, '_setup_count', 0)
        teardown_count = getattr(self, '_teardown_count', 0)
        self.assertEqual(setup_count, 1)
        self.assertEqual(teardown_count, 0)

    def step_step_one(self):
        r'step one'

        setup_count = getattr(self, '_setup_count', 0)
        teardown_count = getattr(self, '_teardown_count', 0)
        self.assertEqual(setup_count, 1)
        self.assertEqual(teardown_count, 0)

    def step_step_two(self):
        r'step two'

        setup_count = getattr(self, '_setup_count', 0)
        teardown_count = getattr(self, '_teardown_count', 0)
        self.assertEqual(setup_count, 2)
        self.assertEqual(teardown_count, 1)
