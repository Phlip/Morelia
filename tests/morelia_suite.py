# -*- coding: utf-8 -*-

#~ from __future__ import generators
import unittest
from unittest import TestCase
import re
import sys
import os
from mock import Mock
pwd = os.path.dirname(os.path.realpath(__file__))
morelia_path = os.path.join(pwd, '../morelia')
sys.path.insert(0, morelia_path)
from morelia import *
from morelia import _something

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

    def test_Scenes_count_Row_dimensions(self):
        self.assemble_scene_table()
        dims = self.table_scene.steps[0].steps[0].count_Row_dimensions()
        self.assertEqual([3, 4], dims)

    def test_Scenes_count_more_Row_dimensions(self):
        self.assemble_scene_table('Step whatever\n')
        dims = self.table_scene.steps[0].steps[0].count_Row_dimensions()
        self.assertEqual([3, 0, 4], dims)

    def test_permutate(self):  #  TODO  remove the title from the dimensions
        expect = [(0, 0, 0), (0, 0, 1), (0, 0, 2), (0, 1, 0), (0, 1, 1), (0, 1, 2), 
                        (0, 2, 0), (0, 2, 1), (0, 2, 2), (0, 3, 0), (0, 3, 1), (0, 3, 2)]
        self.assertEqual(expect, _something([0,4,3]))
        expect = [(0, 0, 0)]
        self.assertEqual(expect, _something([1,1,1]))
        expect = [(0, 0, 0), (0, 0, 1)]
        self.assertEqual(expect, _something([1,1,2]))

    def test_permute_schedule(self):
        expect = _something([3, 0, 4])
        self.assemble_scene_table('Step you betcha\n')
        schedule = self.table_scene.steps[0].steps[0].permute_schedule() # TODO bottle up the self.table_scene.steps[0].steps[0]
        self.assertEqual(expect, schedule)

#  TODO  add Pangolins to the sample data

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
                        And There are 3 vendors
                       When I go to the manage vendors page
                       Then I should see the first 3 vendor names'''

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
        sauce = 'umma | gumma |'  #  TODO  better sauce - Pangolin from Pangea
        row = Row()
        row._parse(sauce, [])
        assert row.predicate == sauce

    def test_parse_feature_Row(self):
        p = Parser()
        p.parse_features(''' | piggy | op |''')
        #print p.steps # TODO

    def assemble_scene_table(self, moar = ''):
        scene = '''Feature: permute tables
                       Scenario: turn one feature into many
                           Given party <zone>
                                | zone  |
                                | beach |
                                | hotel |
                           %sThen hearty <crunk>
                                | crunk | 
                                | work  | 
                                | mall  | 
                                | jail  |''' % moar
        p = Parser()
        self.table_scene = p.parse_features(scene)

    def test_twizzle_moar_Rows(self):
        self.assemble_scene_table('| half-pipe |\n')
        feature = self.table_scene.steps[0]
        scene = feature.steps[0]
        #~ self.assertEqual([1, 1], scene.row_indices)
        #~ scene = feature.steps[1]
        #~ self.assertEqual([2, 1], scene.row_indices)
        #~ scene = feature.steps[2]
        #~ return # TODO
        #~ self.assertEqual([3, 1], scene.row_indices)
        #~ scene = feature.steps[3]
        #~ self.assertEqual([1, 2], scene.row_indices)
        #~ scene = feature.steps[4]
        #~ self.assertEqual([2, 2], scene.row_indices)
        #~ scene = feature.steps[5]
        #~ self.assertEqual([1, 3], scene.row_indices)
        #~ scene = feature.steps[6]
        #~ self.assertEqual([2, 3], scene.row_indices)

#  TODO  squeak if the table has no | in the middle or on the end etc, or if item not found
#  TODO  parse the || as Json/Yaml?

    def test_Rows_find_step_parents(self):
        self.assemble_scene_table()
        given, then, = self.table_scene.steps[0].steps[0].steps
        self.assertEqual(Row, given.steps[0].__class__)
        self.assertEqual(Row,  then.steps[0].__class__)
        self.assertEqual('zone  |', given.steps[0].predicate)
        self.assertEqual('crunk |',  then.steps[0].predicate)

#  TODO  note that default arguments on steps are permitted!

    def assemble_short_scene_table(self, moar = '', even_moar = ''):
        scene = '''Feature: the smoker you drink
                       Scenario: the programmer you get%s
                           Given party <element> in <faction>
                                | faction     | element               |
                                | this  shows | bad but permitted     |
                                | style with  | columns out of order! |%s''' % (even_moar, moar)
        p = Parser()
        self.table_scene = p.parse_features(scene)

#  TODO  permit gaps & comments in tables

    def test_dimensions_with_leading_gaps_are_okay(self):
        self.assemble_short_scene_table('', '\nGiven some dumb step')
        feature = self.table_scene.steps[0]
        #~ self.assertEqual([0, 1], feature.steps[0].row_indices)
        #~ self.assertEqual([0, 2], feature.steps[1].row_indices)

    def test_only_one_table_permutes_only_once(self):
        self.assemble_short_scene_table()
        feature = self.table_scene.steps[0]
        scene = feature.steps[0]
        #~ self.assertEqual([1], scene.row_indices)
        #~ scene = feature.steps[1]
        #~ self.assertEqual([2], scene.row_indices)
        #~ self.assertEqual(2, len(feature.steps))

    def test_only_one_table_permutes_a_little_moar(self):
        self.assemble_short_scene_table('\n| panic | button |')
        feature = self.table_scene.steps[0]
        #~ scene = feature.steps[1]
        #~ self.assertEqual([2], scene.row_indices)
        #~ scene = feature.steps[2]
        #~ self.assertEqual([3], scene.row_indices)
        #~ self.assertEqual(3, len(feature.steps))

    def test_only_one_table_permutes_yet_another_line(self):
        self.assemble_short_scene_table('\n| pet | pangolin |\n| ant | supply |')
        feature = self.table_scene.steps[0]
        #~ scene = feature.steps[2]
        #~ self.assertEqual([3], scene.row_indices)
        #~ scene = feature.steps[3]
        #~ self.assertEqual([4], scene.row_indices)
        #~ self.assertEqual(4, len(feature.steps))

    def test_twizzle_Rows(self):
        self.assemble_scene_table()
        feature = self.table_scene.steps[0]
        scene = feature.steps[0]
        #~ self.assertEqual([1, 1], scene.row_indices)
        #~ scene = feature.steps[1]
        #~ self.assertEqual([2, 1], scene.row_indices)
        #~ scene = feature.steps[2]
        #~ self.assertEqual([1, 2], scene.row_indices)
        #~ scene = feature.steps[3]
        #~ self.assertEqual([2, 2], scene.row_indices)
        #~ scene = feature.steps[4]
        #~ self.assertEqual([1, 3], scene.row_indices)
        #~ scene = feature.steps[5]
        #~ self.assertEqual([2, 3], scene.row_indices)

#  TODO  decorate exceptions failures with their source feature lines
#  TODO  COMMENTS!!!
#  TODO  respect the tests' verbosity levels

    def test_twizzle_gapped_Rows(self):
        self.assemble_scene_table('Step whatever\n')
        feature = self.table_scene.steps[0]
        scene = feature.steps[0]
        #~ self.assertEqual([1,0,1], scene.row_indices)
        #~ scene = feature.steps[1]
        #~ self.assertEqual([2,0,1], scene.row_indices)
        #~ scene = feature.steps[2]
        #~ self.assertEqual([1,0,2], scene.row_indices)

    def step_my_milkshake(self, youth = 'boys', article = 'the'):
        'my milkshake brings all the (boys|girls|.youth.) to (.*) yard'
        self.youth = youth  #  TODO  is "youth" still needed?
    
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
        self.assertEqual(('girls', 'the'), step.matches)

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

    #~ def test_evaluate_unfound(self):
        #~ Parser().parse_file(pwd + '/nada.feature').evaluate(self)
        
    def test_evaluate_file(self):
        Parser().parse_file(pwd + '/morelia.feature').evaluate(self)

    def step_adventure_of_love_love_and_culture_(self):
        "adventure of love - love and <culture>"        # TODO

    def step_Moralia_evaluates_this(self):
        "Moralia evaluates this"

    def step__culture_contains_radio_g_string_battery_driven_(self):
        "\"culture\" contains ['radio', 'g-string', 'battery', 'driven']"

        # code


    def toast_report_file(self):
        Parser().parse_file(pwd + '/morelia.feature').report(self)
        
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


