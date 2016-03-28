# -*- coding: utf-8 -*-
import os
from unittest import TestCase

from morelia.decorators import tags
from morelia.parser import Parser

pwd = os.path.dirname(os.path.realpath(__file__))


@tags(['acceptance'])
class CommentsTest(TestCase):

    def test_comments(self):
        filename = os.path.join(pwd, 'features/comments.feature')
        ast = Parser().parse_file(filename)
        ast.evaluate(self, show_all_missing=True)

    def step_I_have_some_comment_after_step_without_table(self):
        r'I have some comment after step without table'

        pass

    def step_I_have_interpolated_data_from_table(self, data):
        r'I have interpolated (.+) from table'

        pass

    def step_I_execute_this_scenario(self):
        pass

    def step_scenario_will_pass(self):
        assert True
