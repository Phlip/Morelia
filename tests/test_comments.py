# -*- coding: utf-8 -*-
import os
from unittest import TestCase

from morelia import run
from morelia.decorators import tags

pwd = os.path.dirname(os.path.realpath(__file__))


@tags(['acceptance'])
class CommentsTest(TestCase):

    def test_comments(self):
        filename = os.path.join(pwd, 'features/comments.feature')
        run(filename, self)

    def step_scenario_will_pass(self):
        assert True

    def step_I_put_some_comment_after_step_on_separate_line(self):
        pass

    def step_I_put_comment_between_rows_of_table(self):
        pass

    def step_I_won_t_have_comment_in_interpolated_data_from_table(self, data):
        r'I won\'t have comment in interpolated (.+) from table'
        self.assertNotIn('#', data)
