# -*- coding: utf-8 -*-

import unittest
from unittest import TestCase
import re
import sys
import os
pwd = os.path.dirname(os.path.realpath(__file__))
morelia_path = os.path.join(pwd, '../morelia')
sys.path.insert(0, morelia_path)
# from morelia import *
from morelia.base import (Parser, Feature, Scenario, Given, Comment, Step, Row,
                          And, When, Then, Viridis, TestVisitor, _permute_indices)
from morelia.i18n import TRANSLATIONS
from morelia.utils import to_unicode

#  CONSIDER  same order as morelia.feature, & vice-versa
zones = []
crunks = []
factions = []
elements = []


class MoreliaSuite(TestCase):

    def step_I_have_entered_a_number_into_the_calculator(self, number):
        r'I have entered (\d+) into the calculator'

        if not hasattr(self, 'stack'):
            self.stack = []
        self.stack.append(int(number))

    def step_I_press_add(self):
        self.result = sum(self.stack)

    def step_the_result_should_be_on_the_screen(self, number):
        "the result should be (\d+) on the screen"

        self.assertEqual(int(number), self.result)

    def _get_language(self):
        return None

    def test_feature(self):
        language = self._get_language()
        input = '%s: prevent wild animals from eating us' % self.feature_keyword
        steps = Parser(language=language).parse_feature(input)
        step = steps[0]
        assert step.__class__ == Feature
        self.assertEqual(step.concept, 'Feature')
        self.assertEqual(step.predicate, 'prevent wild animals from eating us')

    def test_scenario(self):
        input = '%s: range free Vegans' % self.scenario_keyword
        language = self._get_language()
        steps = Parser(language=language).parse_feature(input)
        step = steps[0]
        assert step.__class__ == Scenario
        self.assertEqual(step.concept, 'Scenario')
        self.assertEqual(step.predicate, 'range free Vegans')

    def test___scenario(self):
        input = '  %s: with spacies' % self.scenario_keyword
        language = self._get_language()
        steps = Parser(language=language).parse_feature(input)
        step = steps[0]
        assert step.__class__ == Scenario
        self.assertEqual(step.concept, 'Scenario')
        self.assertEqual(step.predicate, 'with spacies')

    def test_given_a_string_with_given_in_it(self):
        input = '%(given)s a string with Given in it   \n%(and)s another string' % {
            'given': self.given_keyword,
            'and': self.and_keyword,
        }
        language = self._get_language()
        steps = Parser(language=language).parse_feature(input)  # ^ note the spacies
        step = steps[0]
        assert step.__class__ == Given
        self.assertEqual(step.concept, 'Given')
        self.assertEqual(step.predicate, 'a string with Given in it')  # <-- note spacies are gone

    def test_given_a_broken_string_with_excess_spacies(self):
        input = '%s a string with spacies and   \n  another string  ' % self.given_keyword
        language = self._get_language()
        steps = Parser(language=language).parse_feature(input)
        step = steps[0]
        assert step.__class__ == Given
        self.assertEqual(step.concept, 'Given')
        self.assertEqual(step.predicate, 'a string with spacies and\nanother string')

    def test_deal_with_pesky_carriage_returns(self):  # because Morse Code will live forever!
        input = '%s a string with spacies and   \r\n  another string  ' % self.given_keyword
        language = self._get_language()
        steps = Parser(language=language).parse_feature(input)
        step = steps[0]
        assert step.__class__ == Given
        self.assertEqual(step.concept, 'Given')
        self.assertEqual(step.predicate, 'a string with spacies and\nanother string')

    def test_given_a_string_with_a_line_breaker_followed_by_a_keyword(self):
        input = '%(given)s a string \\\n And another string' % {
            'given': self.given_keyword,
            'and': self.and_keyword,
        }
        language = self._get_language()
        steps = Parser(language=language).parse_feature(input)
        assert 1 == len(steps)
        step = steps[0]
        assert step.__class__ == Given
        self.assertEqual(step.concept, 'Given')
        self.assertEqual(step.predicate, 'a string \\\n And another string')

    def test_given_a_string_with_a_line_breaker_followed_by_a_keyword_with_stray_spacies(self):
        input = '%(given)s a string \\  \n And another string, without stray spacies' % {
            'given': self.given_keyword,
            'and': self.and_keyword,
        }
        language = self._get_language()
        steps = Parser(language=language).parse_feature(input)
        assert 1 == len(steps)
        step = steps[0]
        assert step.__class__ == Given
        self.assertEqual(step.concept, 'Given')
        self.assertEqual(step.predicate, 'a string \\\n And another string, without stray spacies')

    def test_feature_with_scenario(self):
        input = '''%(feature)s: Civi-lie-zation
                   %(scenario)s: starz upon tharz bucks''' % {
                'feature': self.feature_keyword,
                'scenario': self.scenario_keyword,
        }
        language = self._get_language()
        steps = Parser(language=language).parse_feature(input)
        step = steps[0]
        assert step.__class__ == Feature
        self.assertEqual(step.concept, 'Feature')
        self.assertEqual(step.predicate, 'Civi-lie-zation')
        step = steps[1]
        assert step.__class__ == Scenario
        self.assertEqual(step.concept, 'Scenario')
        self.assertEqual(step.predicate, 'starz upon tharz bucks')

    # def test_feature_with_lone_comment(self):
    #     input = '''Feature: The Sacred White Llama of the Inca\r
    #                #  I are a comment'''
    #     steps = Parser().parse_feature(input)
    #     assert steps[0].__class__ == Feature

    #     step = steps[1]
    #     assert step.__class__ == Comment
    #     self.assertEqual(step.concept, 'Comment')
    #     self.assertEqual(step.predicate, 'I are a comment')

    def test_feature_with_lone_comment(self):
        input = 'i be a newbie feature'
        language = self._get_language()
        p = Parser(language=language)

        try:
            p.parse_feature(input)
            assert False  # should fail!
        except SyntaxError as e:
            e = e.args[0]
            self.assert_regex_contains(r'File "None", line 1, in', e)
            self.assert_regex_contains(r'\?\?\?: i be a newbie feature', e)
            try:
                feature_name = TRANSLATIONS[language].get('feature', u'Feature')
            except KeyError:
                feature_name = 'Feature'
            else:
                feature_name = feature_name.replace('|', ' or ')
            self.assert_regex_contains(r'feature files must start with a %s' % feature_name, e)

    def test_feature_with_long_comment(self):  # ERGO how to detect shadowed test cases??
        language = self._get_language()
        p = Parser(language=language)

        input = '''%s: The Sacred Giant Mosquito of the Andes
                   #  at http://www.onagocag.com/nazbird.jpg
                        so pay no attention to the skeptics!''' % self.feature_keyword
        try:
            p.parse_feature(input)
            assert False  # should raise a SyntaxError
        except SyntaxError as e:
            self.assert_regex_contains('linefeed in comment', str(e))
            self.assert_regex_contains('line 2', str(e))

        steps = p.steps
        assert steps[0].__class__ == Feature
        step = steps[1]
        assert step.__class__ == Comment
        self.assertEqual(step.concept, 'Comment')

    def pet_scenario(self):
        return '''%(scenario)s: See all vendors
                      %(given)s I am logged in as a user in the administrator role
                        %(and)s There are 3 vendors
                       %(when)s I go to the manage vendors page
                       %(then)s I should see the first 3 vendor names''' % {
            'scenario': self.scenario_keyword,
            'given': self.given_keyword,
            'and': self.and_keyword,
            'when': self.when_keyword,
            'then': self.then_keyword,
        }

    def test_parse_scenario(self):
        scenario = self.pet_scenario()
        language = self._get_language()
        steps = Parser(language=language).parse_feature(scenario)
        step_0, step_1, step_2, step_3, step_4 = steps
        self.assertEqual(step_0.concept, 'Scenario')
        self.assertEqual(step_0.predicate, 'See all vendors')
        self.assertEqual(step_1.concept, 'Given')
        self.assertEqual(step_1.predicate, 'I am logged in as a user in the administrator role')
        self.assertEqual(step_2.concept, 'And')
        self.assertEqual(step_2.predicate, 'There are 3 vendors')
        self.assertEqual(step_3.concept, 'When')
        self.assertEqual(step_3.predicate, 'I go to the manage vendors page')
        self.assertEqual(step_4.concept, 'Then')
        self.assertEqual(step_4.predicate, 'I should see the first 3 vendor names')

    def test_strip_predicates(self):
        language = self._get_language()
        step = Parser(language=language).parse_feature('  %s   gangsta girl   \t     ' % self.given_keyword)[0]
        self.assertEqual(step.concept, 'Given')
        self.assertEqual(step.predicate, 'gangsta girl')

    def test_bond_predicates(self):
        return  # CONSIDER  why test_strip_predicates passes and this croaks???
        language = self._get_language()
        step = Parser(language=language).parse_feature('  %s\n   elf quest   \t     ' % self.given_keyword)[0]
        self.assertEqual(step.concept, 'Given')
        self.assertEqual(step.predicate, 'elf quest')

    def test_scenarios_link_to_their_steps(self):
        language = self._get_language()
        steps = Parser(language=language).parse_feature(self.pet_scenario())
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

    def test_evaluate_step_by_name(self):
        step = Given()._parse('my milkshake')
        self.youth = 'girls'
        step.evaluate(self)
        self.assertEqual('boys', self.youth)

# ####  row zone  #################################

    def test_Row_parse(self):
        sauce = 'buddha | brot |'
        row = Row()
        row._parse(sauce, [])
        assert row.predicate == sauce

    def test_parse_feature_Row(self):
        language = self._get_language()
        p = Parser(language=language)
        p.parse_features(''' | piggy | op |''')
        assert Row == p.steps[0].__class__
        assert p.steps[0].predicate == 'piggy | op |'

    def test_Scenes_count_Row_dimensions(self):
        self.assemble_scene_table()
        dims = self.table_scene.steps[0].steps[0].count_Row_dimensions()
        self.assertEqual([2, 3], dims)

    def test_Scenes_count_more_Row_dimensions(self):
        self.assemble_scene_table('Step whatever\n')
        dims = self.table_scene.steps[0].steps[0].count_Row_dimensions()
        self.assertEqual([2, 0, 3], dims)

    def test_permutate(self):
        expect = [(0, 0, 0), (0, 0, 1), (0, 0, 2), (0, 1, 0), (0, 1, 1),
                  (0, 1, 2), (0, 2, 0), (0, 2, 1), (0, 2, 2), (0, 3, 0),
                  (0, 3, 1), (0, 3, 2)]
        self.assertEqual(expect, _permute_indices([0, 4, 3]))
        expect = [(0, 0, 0)]
        self.assertEqual(expect, _permute_indices([1, 1, 1]))
        expect = [(0, 0, 0), (0, 0, 1)]
        self.assertEqual(expect, _permute_indices([1, 1, 2]))

    def assemble_scene_table_source(self, moar=''):
        return '''%(feature)s: permute tables
                       %(scenario)s: turn one feature into many
                           %(given)s party <zone>
                                | zone  |
                                | beach |
                                | hotel |
                           %(moar)s%(then)s hearty <crunk>
                                | crunk |
                                | work  |
                                | mall  |
                                | jail  |''' % {
            'moar': moar,
            'feature': self.feature_keyword,
            'scenario': self.scenario_keyword,
            'given': self.given_keyword,
            'then': self.then_keyword,
        }

    def assemble_scene_table(self, moar=''):
        scene = self.assemble_scene_table_source(moar)
        language = self._get_language()
        p = Parser(language=language)
        self.table_scene = p.parse_features(scene)

    def test_permute_schedule(self):
        expect = _permute_indices([2, 0, 3])  # NOTE:  by rights, 0 should be -1
        self.assemble_scene_table('Step you betcha\n')
        scenario = self.table_scene.steps[0].steps[0]
        schedule = scenario.permute_schedule()
        self.assertEqual(expect, schedule)

    def test_evaluate_permuted_schedule(self):
        self.assemble_scene_table('Step flesh is weak\n')
        scenario = self.table_scene.steps[0].steps[0]
        visitor = TestVisitor(self)
        global crunks, zones
        crunks = []
        zones = []
        scenario.row_indices = [1, 0, 2]
        scenario.evaluate_test_case(visitor)
        self.assertEqual('hotel', visitor.suite.got_party_zone)
        self.assertEqual('jail', visitor.suite.got_crunk)

    def test_another_two_dimensional_table(self):
        global crunks, zones
        crunks = []
        zones = []
        scene = self.assemble_scene_table_source('Step my milkshake brings all the boys to the yard\n')
        language = self._get_language()
        Parser(language=language).parse_features(scene).evaluate(self)
        self.assertEqual(['work', 'mall', 'jail', 'work', 'mall', 'jail'], crunks)
        self.assertEqual(['beach', 'beach', 'beach', 'hotel', 'hotel', 'hotel'], zones)

    def assemble_multiple_whens(self):
        return '''%(scenario)s: Split When Blocks
                      %(given)s some setup
                       %(when)s a first trigger occurs
                       %(then)s something good happens
                       %(when)s another trigger occurs
                       %(then)s something else happens''' % {
            'scenario': self.scenario_keyword,
            'given': self.given_keyword,
            'when': self.when_keyword,
            'then': self.then_keyword,
        }

#  TODO  what happens when a scene has 2 tables and it pulls keywords from either one?
#  TODO  what happens when a scene has different tables in different When blocks?

    def test_parse_multiple_whens(self):
        scenario = self.assemble_multiple_whens()
        language = self._get_language()
        steps = Parser(language=language).parse_feature(scenario)  # TODO  test that a non-double-When Scenario gives a flat schedule
        scene, step_1, step_2, step_3, step_4, step_5 = steps
        assert scene.concept == 'Scenario'
        assert [[0, 1, 2], [0, 3, 4]] == scene.step_schedule()  # TODO  mix step schedules and row schedules! (-:
        # TODO  better object model! assert 2 == step_0.count_whens()

    def test_harvest(self):
        r = Row()

        def harvest(predicate):
            r.predicate = predicate
            return r.harvest()

        self.assertEqual(['crock', 'of'], harvest('crock | of'))
        self.assertEqual(['crock', 'of'], harvest('crock | of |'))

        # CONSIDER  document you gotta take the \ out yourself

        self.assertEqual(['crane \| wife', 'three'], harvest('crane \| wife | three'))

    def step_party_zone(self, zone):  # CONSIDER  prevent collision with another "step_party"
        r'party (\w+)'  # CONSIDER  illustrate how the patterns here form testage too

        self.got_party_zone = zone
        global zones
        zones.append(zone)

    def step_flesh_is_weak(self):
        pass

    def step_hearty_crunk_(self, crunk):
        r'hearty (\w+)'

        global crunks
        crunks.append(crunk)
        self.got_crunk = crunk

#  TODO  squeak if the table item ain't found
#  TODO  respect the tests' verbosity levels
#  CONSIDER  note that default arguments on steps are permitted!
#  CONSIDER  parse the || as Json/Yaml? - permit gaps & comments in tables

    def test_Rows_find_step_parents(self):
        self.assemble_scene_table()
        given, then, = self.table_scene.steps[0].steps[0].steps
        self.assertEqual(Row, given.steps[0].__class__)
        self.assertEqual(Row, then.steps[0].__class__)
        self.assertEqual('zone  |', given.steps[0].predicate)
        self.assertEqual('crunk |', then.steps[0].predicate)

    def assemble_short_scene_table(self):
        #  TODO  warn about bad but permitted style -- with | columns | out of order!
            #  TODO  reporter should beautify || markers!
        return '''%(feature)s: the smoker you drink
                    %(scenario)s: the programmer you get
                      %(given)s party <element> from <faction>

                                | faction   | element  |

                                | Pangolin  | Pangea   |
                                | Glyptodon | Laurasia |''' % {
            'feature': self.feature_keyword,
            'scenario': self.scenario_keyword,
            'given': self.given_keyword,
        }

    def test_two_dimensional_table(self):
        global elements, factions
        elements = []
        factions = []
        language = self._get_language()
        Parser(language=language).parse_features(self.assemble_short_scene_table()).evaluate(self)
        self.assertEqual([['Pangolin', 'Glyptodon'], ['Pangea', 'Laurasia']], [factions, elements])

    def test_two_dimensional_table_reconstruction(self):
        language = self._get_language()
        p = Parser(language=language).parse_features(self.assemble_short_scene_table())
        step = p.steps[0].steps[0].steps[0]
        self.assertEqual(step.concept + ': ' + step.predicate, step.reconstruction().strip())

    def step_party_element_from_faction(self, element, faction):
        r'party (\w+) from (\w+)'
        # TODO  don't default to this "party <element> in <faction>"

        global elements, factions
        factions.append(faction)
        elements.append(element)

    def step_my_milkshake(self, youth='boys', article='the'):
        r'my milkshake brings all the (boys|girls) to (.*) yard'

        self.youth = youth

    def step_exceptional(self):
        x = 1 / 0  # noqa guilty pleasure for programmers!

    def test_handle_exceptions(self):
        s = Step()

        s.concept = 'Given'
        s.predicate = 'exceptional'
        s.line_number = 42
        visitor = TestVisitor(self)

        try:
            s.test_step(visitor)
            assert False  # should raise!
        except ZeroDivisionError as e:
            assert 'Given: exceptional' in str(e)

    def test_find_step_by_name(self):
        step = Given()._parse('my milkshake')
        step.find_by_name(self)
        expect = self.step_my_milkshake
        self.assertEqual(expect, step.method)

    def test_find_step_by_doc_string(self):
        step = And()._parse('my milkshake brings all the boys to the yard')
        step.find_by_doc_string(self)
        expect = self.step_my_milkshake
        self.assertEqual(expect, step.method)

    def test_find_step_with_match(self):
        step = When()._parse('my milkshake brings all the girls to the yard')
        step.find_by_doc_string(self)
        self.assertEqual(('girls', 'the'), step.matches)

    def test_step_not_found(self):
        step = Then()._parse('not there')
        assert None == step.find_by_name(self)

    def step_fail_without_enough_function_name(self):
        step = And()._parse('my milk')
        assert None == step.find_by_name(self)

    def step_fail_step_without_enough_doc_string(self):
        step = Given()._parse("brings all the boys to the yard it's better than yours")
        assert None == step.find_by_doc_string(self)

    def step_evaluate_step_by_doc_string(self):
        step = Given()._parse('my milkshake brings all the girls to a yard')
        self.youth = 'boys'
        step.evaluate(self)
        self.assertEqual('girls', self.youth)  # Uh...

    def step_multiline_predicate(self):
        feature = '%s umma\ngumma' % self.given_keyword
        language = self._get_language()
        steps = Parser(language=language).parse_feature(feature)
        self.assertEqual('umma\ngumma', steps[0].predicate)

    def test_step_multiline_predicate(self):
        feature = '%s multiline predicate' % self.when_keyword
        language = self._get_language()
        steps = Parser(language=language).parse_feature(feature)
        steps[0].evaluate(self)

# CONSIDER use the suite._testMethodDoc to get the doc()! (and what can it do??)
# CONSIDER  use suite.fail instead of raise

#    def test_evaluate_unfound(self):  CONSIDER   real test outa this
#       Parser().parse_file(pwd + '/nada.feature').evaluate(self)

    def test_record_filename(self):
        language = self._get_language()
        filename = pwd + '/morelia%s.feature' % (language or '')
        thang = Parser(language=language).parse_file(filename)
        feature = thang.steps[0]
        assert feature.__class__ == Feature
        assert feature.filename == filename
        step = feature.steps[3].steps[1]
        assert filename == step.get_filename()

    def test_format_faults_like_python_errors(self):
        language = self._get_language()
        filename = pwd + '/morelia%s.feature' % (language or '')
        thang = Parser(language=language).parse_file(filename)
        step = thang.steps[0].steps[3].steps[1]
        assert filename == step.get_filename()
        omen = 'The Alpine glaciers move'
        diagnostic = step.format_fault(omen)
        parent_reconstruction = step.parent.reconstruction().replace('\n', '\\n')
        reconstruction = step.reconstruction().replace('\n', '\\n')

        expect = '\n  File "%s", line %s, in %s\n    %s\n%s' % \
            (step.get_filename(), step.line_number, parent_reconstruction, reconstruction, omen)

        assert expect == diagnostic

    def test_evaluate_file(self):
        language = self._get_language()
        thang = Parser(language=language).parse_file(pwd + '/morelia%s.feature' % (language or ''))
        thang.evaluate(self)

    def setUp(self):
        self.culture = []
        self.feature_keyword = 'Feature'
        self.scenario_keyword = 'Scenario'
        self.given_keyword = 'Given'
        self.then_keyword = 'Then'
        self.when_keyword = 'When'
        self.and_keyword = 'And'

    def step_adventure_of_love_love_and_culture_(self, culture):
        r'adventure of love - love and (.+)'

        self.culture.append(culture)
        self.concept = self.step.concept

    def step_Moralia_evaluates_this(self):
        pass

    def step_culture_contains(self, arguments):
        r'"culture" contains (.*)'

        self.assertEqual(1, arguments.count(self.culture[0]))
        self.assertEqual(1, len(self.culture))

    def _xml_to_tree(self, xml):
        from lxml import etree
        self._xml = xml

        try:
            if '<html' in xml[:200]:
                return etree.HTML(xml)
            else:
                return etree.XML(xml)

        except ValueError:  # TODO don't rely on exceptions for normal control flow
            tree = xml
            self._xml = str(tree)  # CONSIDER does this reconstitute the nested XML ?
            return tree

    def assert_xml(self, xml, xpath, **kw):
        'Check that a given extent of XML or HTML contains a given XPath, and return its first node'

        tree = self._xml_to_tree(xml)
        nodes = tree.xpath(xpath)
        self.assertTrue(len(nodes) > 0, xpath + ' not found in ' + self._xml)
        node = nodes[0]
        if kw.get('verbose', False):
            self.reveal_xml(node)  # "here have ye been? What have ye seen?"--Morgoth
        return node

    def test_report_file(self):
        language = self._get_language()
        thang = Parser(language=language).parse_file(pwd + '/morelia%s.feature' % (language or ''))
        div_count = len(thang.steps[0].steps)  # CONSIDER  this off-by-one and on-by-one; dunno why, needs fixed

        rep = thang.report(self).string
        once = 'when did Bow Wow Wow become classic rock'
        assert 1 == rep.count(once)

        html = '<xml>' + rep + '</xml>'
        # open('/tmp/yo.html', 'w').write(html.encode('utf-8'))
        # ERGO assert_xml with <html> forgives - crack down on that!

        self.assert_xml(html, '/xml[ count(descendant::div) > %i ]' % (div_count - 1))
        #  os.system('firefox /home/phlip/morelia/yo.html &')
        # os.system('konqueror  /home/phlip/morelia/yo.html &')

    def step_a_feature_file_with_contents(self, file_contents):
        r'a feature file with "([^"]+)"'
        self.file_contents = file_contents

    # def step_wikked_(self):
    # '''wikked!
    # '''
    #  TODO get rid of linefeeds in the suggestions
    # assert False

    def step_Moralia_evaluates_the_file(self):
        self.diagnostic = None
        self.steps = []

        try:
            language = self._get_language()
            p = Parser(language=language)
            self.file_contents.replace('\\#', '#')  # note - this is how to unescape characters - DIY
            p.parse_features(self.file_contents).evaluate(self)
            self.steps = p.steps
        except AssertionError as e:
            self.diagnostic = str(e)

    def step_it_prints_a_diagnostic(self, sample):
        r'it prints a diagnostic containing "([^"]+)"'

        self.assert_regex_contains(re.escape(sample), self.diagnostic)

    def step_the_second_line_contains(self, docstring):
        r'the second line contains "([^"]+)"'

        self.assert_regex_contains(re.escape(docstring), self.diagnostic)

    def step_it_contains_1_step(self):
        r'it contains 1 step'

        self.assertEqual(1, len(self.steps))

    def step_the_step_concept_is_(self, concept):
        r'the step concept is (.+)'

        self.assertEqual(concept, self.concept)

    def step_a_source_file_with_a_Given_(self, predicate):
        r'a source file with a (.+)'

        self.predicate = predicate.replace('\\n', '\n')

    def step_we_evaluate_the_file(self):
        r'we evaluate the file'

        self.viridis = Viridis()
        self.suggestion = self.viridis.suggest_doc_string(self.predicate)

    def step_we_convert_it_into_a_(self, suggestion):
        r'we convert it into a (.+)'

        self.assertEqual(suggestion, self.suggestion)

    def step_add_extra_arguments(self, extra=''):  # TODO  blank columns should exist!
        r'add (.+) arguments'

        self.assertEqual(extra, self.viridis.extra_arguments)

    def step_a_file_contains_statements_produce_diagnostics_(self, statements, diagnostics):
        r'a file contains (.+), it produces (.+)'

        try:
            statements = statements.replace('\\n', '\n')  # CONSIDER  document this is how you paint linefeedage
            statements = statements.replace('\\', '')  # CONSIDER document this is how you paint reserved words
            # diagnostics = diagnostics.replace('\\', '')  #  CONSIDER  document this is how you escape pipes
            # print len(self.step.steps)  #  CONSIDER  document this as the way to hit the whole table
            language = self._get_language()
            p = Parser(language=language).parse_features(statements)
            p.evaluate(self)
            raise Exception('we expect syntax errors here')
        except (SyntaxError, AssertionError) as e:
            e = e.args[0]
            beef, squeak = diagnostics.split(', line ')
            squeak = 'line ' + squeak
            self.assert_regex_contains(re.escape(beef), e)
            self.assert_regex_contains(re.escape(squeak), e)

    def step_errors(self):
        raise SyntaxError('no, you!')

    def assert_regex_contains(self, pattern, string, flags=None):
        flags = flags or 0
        pattern = to_unicode(pattern)
        string = to_unicode(string)
        diagnostic = u'"%s" not found in "%s"' % (pattern, string)
        self.assertTrue(re.search(pattern, string, flags) is not None, diagnostic)

# Scenario: Leading # marks comment lines.
    # (Warning: Only leading marks are respected for now!)
    # Given a feature file with "When something
    # \# Given nothing"
    # When Moralia evaluates the file
    # Then it contains 1 step
    # And the first step contains "something"
    # And the first step does not contain "nothing"

# CONSIDER  count test cases correctly regarding entire batch - if pyUnit's architecture permits


class PLMoreliaSuite(MoreliaSuite):

    def setUp(self):
        self.culture = []
        self.feature_keyword = 'Właściwość'
        self.scenario_keyword = 'Scenariusz'
        self.given_keyword = 'Zakładając, że'
        self.then_keyword = 'Wtedy'
        self.when_keyword = 'Gdy'
        self.and_keyword = 'I'

    def _get_language(self):
        return 'pl'

    def test_language_directive(self):
        input = '# language: pl\n%s: prevent wild animals from eating us' % self.feature_keyword
        steps = Parser().parse_feature(input)
        step = steps[0]
        assert step.__class__ == Feature
        self.assertEqual(step.concept, 'Feature')
        self.assertEqual(step.predicate, 'prevent wild animals from eating us')


if __name__ == '__main__':
    unittest.main()  # NOTE  this seems to return the correct shell value
