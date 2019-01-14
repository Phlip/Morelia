# -*- coding: utf-8 -*-

"""Regression tests."""
import os
import six
from unittest import TestCase

from morelia import run
from morelia.decorators import tags

pwd = os.path.dirname(os.path.realpath(__file__))


@tags(['acceptance', 'regression'])
class SetUpTearDownTest(TestCase):

    """Test for recreating bug with multiple setUp/tearDown call."""

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
        """Check for multiple setUp/tearDown calls."""
        filename = os.path.join(pwd, 'features/setupteardown.feature')
        run(filename, self)

    def test_many_test_methods(self):
        """Check setUp/tearDown when many tests in one TestCase."""
        filename = os.path.join(pwd, 'features/setupteardown.feature')
        run(filename, self)

    def test_not_morelia_test(self):
        """Check if influcence on non morelia tests."""
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


@tags(['acceptance', 'regression'])
class EncodingErrorInTraceback(TestCase):

    def test_should_report_on_all_failing_scenarios(self):
        filename = os.path.join(pwd, 'features/encoding_error_in_regression.feature')
        if six.PY2:
            self.assertRaisesRegexp(AssertionError, 'Given Zażółć gęślą jaźń', run, filename, self)
        else:
            self.assertRaisesRegex(AssertionError, 'Given Zażółć gęślą jaźń', run, filename, self)

    def step_failing(self):
        r'Zażółć gęślą jaźń'

        assert False, u'Zażółć gęślą jaźń Эх, чужак! Общий съём цен шляп (юфть) — вдрызг!'
