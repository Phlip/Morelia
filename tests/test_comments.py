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

    def step_I_have_some_comment_after_step_without_table(self):
        r'I have some comment after step without table'
        pass

    def step_I_have_interpolated_data_from_table(self, data):
        r'I have interpolated (.+) from table'
        self.assertNotIn('#', data)

    def step_I_execute_this_scenario(self):
        pass

    def step_scenario_will_pass(self):
        assert True

    def step_I_have_some_comment_after_step_on_separate_line(self):
        pass

    def step_I_have_some_comment_after_step_in_the_same_line_like_this_this_one(self):
        r'I have some comment after step in the same line'
        pass

    def step_I_have_some_comment_after_row_in_table(self):
        pass
