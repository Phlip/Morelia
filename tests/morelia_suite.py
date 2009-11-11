# -*- coding: utf-8 -*-

import unittest
from unittest import TestCase
import re
import sys
import os
pwd = os.path.dirname(os.path.realpath(__file__))
morelia_path = os.path.join(pwd, '../morelia')
sys.path.insert(0, morelia_path)
from morelia import *

 #  TODO  cron order already!


class MoreliaTest(TestCase):

    def test_feature(self):
        input = 'Feature: prevent wild animals from eating us'
        steps = Parser().parse_feature(input)
        step = steps[0]

        assert step.__class__ == Feature
        self.assertEqual(step.concept, 'Feature')
        self.assertEqual(step.predicate, 'prevent wild animals from eating us')

    def test_scenario(self):
        input = 'Scenario: range free Vegans'
        steps = Parser().parse_feature(input)
        step = steps[0]
        assert step.__class__ == Scenario
        self.assertEqual(step.concept, 'Scenario')
        self.assertEqual(step.predicate, 'range free Vegans')
        
    def test___scenario(self):
        input = '  Scenario: with spacies'
        steps = Parser().parse_feature(input)
        step = steps[0]
        assert step.__class__ == Scenario
        self.assertEqual(step.concept, 'Scenario')
        self.assertEqual(step.predicate, 'with spacies')

    def test_given_a_string_with_given_in_it(self):
        input = 'Given a string with Given in it\nAnd another string'
        steps = Parser().parse_feature(input)
        step = steps[0]
        #~ print steps[1].concept
        #~ print steps[1].predicate
        assert step.__class__ == Given
        self.assertEqual(step.concept, 'Given')
        self.assertEqual(step.predicate, 'a string with Given in it')

    def test_feature_with_scenario(self):
        input = '''Feature: Civi-lie-zation
                        Scenario: starz upon tharz bucks'''
        steps = Parser().parse_feature(input)
        step = steps[0]
        assert step.__class__ == Feature
        self.assertEqual(step.concept, 'Feature')
        self.assertEqual(step.predicate, 'Civi-lie-zation')
        step = steps[1]
        assert step.__class__ == Scenario
        self.assertEqual(step.concept, 'Scenario')
        self.assertEqual(step.predicate, 'starz upon tharz bucks')

    def pet_scenario(self):
        return '''Scenario: See all vendors
                      Given I am logged in as a user in the administrator role
                      And   There are 3 vendors
                      When  I go to the manage vendors page
                      Then  I should see the first 3 vendor names'''

    def test_parse_scenario(self):
        scenario = self.pet_scenario()
        steps = Parser().parse_feature(scenario)
        step_0, step_1, step_2, step_3, step_4 = steps
        self.assertEqual(step_0.concept, 'Scenario')
        self.assertEqual(step_0.predicate, 'See all vendors')
        self.assertEqual(step_1.concept, 'Given')
        self.assertEqual(step_1.predicate,     'I am logged in as a user in the administrator role')
        self.assertEqual(step_2.concept, 'And')
        self.assertEqual(step_2.predicate,   'There are 3 vendors')
        self.assertEqual(step_3.concept, 'When')
        self.assertEqual(step_3.predicate,    'I go to the manage vendors page')
        self.assertEqual(step_4.concept, 'Then')
        self.assertEqual(step_4.predicate,    'I should see the first 3 vendor names')

    def test_strip_predicates(self):
        step = Parser().parse_feature('  Given   gangsta girl   \t     ')[0]
        self.assertEqual(step.concept, 'Given')
        self.assertEqual(step.predicate, 'gangsta girl')

    def test_bond_predicates(self):
        step = Parser().parse_feature('  Given\n   elf quest   \t     ')[0]
        self.assertEqual(step.concept, 'Given')
        self.assertEqual(step.predicate, 'elf quest')

    def test_scenarios_link_to_their_steps(self):
        steps = Parser().parse_feature(self.pet_scenario())
        scenario, step_1, step_2, step_3, step_4 = steps
        self.assertEqual([step_1, step_2, step_3, step_4], scenario.steps)

    def test_how_to_identify_trees_from_quite_a_long_distance_away(self):
        assert Given != Step
        assert issubclass(Given, Step)
        assert issubclass(Given, Given)
        assert not issubclass(Scenario, Given)

    def test_i_look_like(self):
        self.assertEqual('Step', Step().i_look_like())
        self.assertEqual('Given', Given().i_look_like())
        self.assertEqual('\\|', Row().i_look_like())

    def test_Row_parse(self):
        sauce = 'umma | gumma |'  #  TODO  better sauce
        row = Row()
        row._parse(sauce, [])
        assert row.predicate == sauce

    def test_parse_feature_Row(self):
        p = Parser()
        p.parse_features(''' | piggy | op |''')
        print p.steps

    def test_Rows_find_step_parents(self):
        p = Parser()
        
        p = p.parse_features('''Given party <zone>
                                                    | beach | hotel |
                                              Then hearty <zone>
                                                    | work | jail |''')

        given, x, then, y = p.steps
        self.assertEqual(Row, given.steps[0].__class__)
        self.assertEqual(Row, then.steps[0].__class__)
        self.assertEqual('beach | hotel |', given.steps[0].predicate)
        self.assertEqual('work | jail |', then.steps[0].predicate)

    def step_my_milkshake(self, youth = 'boys', article = 'the', TODO_take_this_out = ''):
        'my milkshake brings all the (boys|girls|.youth.) to (.*) yard(.*)'
        self.youth = youth
    
    def test_find_step_by_name(self):
        step = Given('my milkshake')
        method = step.find_by_name(self)
        expect = self.step_my_milkshake
        self.assertEqual(expect, method)

    def test_find_step_by_doc_string(self):
        step = Given('my milkshake brings all the boys to the yard')
        method = step.find_by_doc_string(self)
        expect = self.step_my_milkshake
        self.assertEqual(expect, method)

    def test_find_step_with_match(self):
        step = Given('my milkshake brings all the girls to the yard')
        step.find_by_doc_string(self)
        self.assertEqual(('girls', 'the', ''), step.matches)  #  TODO  the , '' will go away!

    def test_step_not_found(self):
        step = Given('not there')
        assert None == step.find_by_name(self)
        
    def step_fail_without_enough_function_name(self):
        step = Given('my milk')
        assert None == step.find_by_name(self)
        
    def step_fail_step_without_enough_doc_string(self):
        step = Given("brings all the boys to the yard it's better than yours")
        assert None == step.find_by_doc_string(self)
        
    def step_evaluate_step_by_doc_string(self):
        step = Given('my milkshake brings all the girls to a yard')
        self.youth = 'boys'
        step.evaluate(self)
        self.assertEqual('girls', self.youth)  # Uh...

    def test_evaluate_step_by_name(self):
        step = Given('my milkshake')
        self.youth = 'girls'
        step.evaluate(self)
        self.assertEqual('boys', self.youth)

    def step_multiline_predicate(self):
        feature = 'Given umma\ngumma'
        steps = Parser().parse_feature(feature)
        self.assertEqual('umma\ngumma', steps[0].predicate)

    def test_step_multiline_predicate(self):
        feature = 'When multiline predicate'
        steps = Parser().parse_feature(feature)
        steps[0].evaluate(self)

    def test_evaluate_file(self):
        Parser().parse_file(pwd + '/morelia.feature').evaluate(self)
        
    def toast_report_file(self):
        Parser().parse_file('morelia.features').report(self)
        
    def step_a_feature_file_with_contents(self, file_contents):
        "a feature file with \"([^\"]+)\""
        self.file_contents = file_contents
        
    #~ def step_wikked_(self):
        #~ '''wikked!
    #~ '''
#~ #  TODO get rid of linefeeds in the suggestions
        #~ assert False
        
    def step_Moralia_evaluates_the_file(self):
        self.diagnostic = None
        
        try:
            p = Parser()
            p.parse_features(self.file_contents).evaluate(self)
            self.steps = p.steps
        except AssertionError, e: 
            self.diagnostic = str(e)

    def step_it_prints_a_diagnostic(self, sample):
        "it prints a diagnostic containing \"([^\"]+)\""
        self.diagnostic.index(sample)  #  CONSIDER  clearer diagnostics!!
        #self.assertTrue(diagnostic, 'foo')
        
    def step_the_second_line_contains(self, docstring):
        "the second line contains \"([^\"]+)\""
        self.diagnostic.split('\n')[4].index(docstring)


#~ TODO Scenario: Leading # marks comment lines.
    #~ (Warning: Only leading marks are respected for now!)
    #~ Given a feature file with "When something
                               #~ # Given nothing"
    #~ When Moralia evaluates the file
    #~ Then it contains 1 step
    #~ And the first step contains "something"

#  TODO  count test cases correctly regarding entire batch
#  TODO  auto-tables
#  TODO  escape string catch

if __name__ == '__main__':
      unittest.main()  #  NOTE  this seems to return the correct shell value


