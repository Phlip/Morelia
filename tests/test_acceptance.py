# -*- coding: utf-8 -*-
import os
import re
import sys

from unittest import TestCase

from morelia.decorators import tags
from morelia.parser import Parser
from morelia.grammar import (Feature, Scenario, Given, Comment, Step, Row,
                             And, When, Then, _permute_indices)
from morelia.exceptions import MissingStepError
from morelia.formatters import NullFormatter
from morelia.i18n import TRANSLATIONS
from morelia.matchers import RegexpStepMatcher, MethodNameStepMatcher
from morelia.visitors import TestVisitor
from morelia.utils import to_unicode


pwd = os.path.dirname(os.path.realpath(__file__))
morelia_path = os.path.join(pwd, '../morelia')
sys.path.insert(0, morelia_path)

zones = []
crunks = []
factions = []
elements = []


@tags(['acceptance'])
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
        self.assertEqual(step.keyword, self.feature_keyword)
        self.assertEqual(step.predicate, 'prevent wild animals from eating us')

    def test_scenario(self):
        input = '%s: range free Vegans' % self.scenario_keyword
        language = self._get_language()
        steps = Parser(language=language).parse_feature(input)
        step = steps[0]
        assert step.__class__ == Scenario
        self.assertEqual(step.keyword, self.scenario_keyword)
        self.assertEqual(step.predicate, 'range free Vegans')

    def test___scenario(self):
        input = '  %s: with spacies' % self.scenario_keyword
        language = self._get_language()
        steps = Parser(language=language).parse_feature(input)
        step = steps[0]
        assert step.__class__ == Scenario
        self.assertEqual(step.keyword, self.scenario_keyword)
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
        self.assertEqual(step.keyword, self.given_keyword)
        self.assertEqual(step.predicate, 'a string with Given in it')  # <-- note spacies are gone

    def test_given_a_broken_string_with_excess_spacies(self):
        input = '%s a string with spacies and   \n  another string  ' % self.given_keyword
        language = self._get_language()
        steps = Parser(language=language).parse_feature(input)
        step = steps[0]
        assert step.__class__ == Given
        self.assertEqual(step.keyword, self.given_keyword)
        self.assertEqual(step.predicate, 'a string with spacies and\nanother string')

    def test_deal_with_pesky_carriage_returns(self):  # because Morse Code will live forever!
        input = '%s a string with spacies and   \r\n  another string  ' % self.given_keyword
        language = self._get_language()
        steps = Parser(language=language).parse_feature(input)
        step = steps[0]
        assert step.__class__ == Given
        self.assertEqual(step.keyword, self.given_keyword)
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
        self.assertEqual(step.keyword, self.given_keyword)
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
        self.assertEqual(step.keyword, self.given_keyword)
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
        self.assertEqual(step.keyword, self.feature_keyword)
        self.assertEqual(step.predicate, 'Civi-lie-zation')
        step = steps[1]
        assert step.__class__ == Scenario
        self.assertEqual(step.keyword, self.scenario_keyword)
        self.assertEqual(step.predicate, 'starz upon tharz bucks')

    # def test_feature_with_lone_comment(self):
    #     input = '''Feature: The Sacred White Llama of the Inca\r
    #                #  I are a comment'''
    #     steps = Parser().parse_feature(input)
    #     assert steps[0].__class__ == Feature

    #     step = steps[1]
    #     assert step.__class__ == Comment
    #     self.assertEqual(step.keyword, 'Comment')
    #     self.assertEqual(step.predicate, 'I are a comment')

    def test_feature_with_lone_comment(self):
        input = 'i be a newbie feature'
        language = self._get_language()
        p = Parser(language=language)

        try:
            p.parse_feature(input)
            assert False  # should fail!  # pragma: nocover
        except SyntaxError as e:
            e = e.args[0]
            try:
                feature_name = TRANSLATIONS[language].get('feature', self.feature_keyword)
            except KeyError:
                feature_name = self.feature_keyword
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
            assert False  # should raise a SyntaxError  # pragma: nocover
        except SyntaxError as e:
            self.assert_regex_contains('linefeed in comment', str(e))
            self.assert_regex_contains('line 2', str(e))

        steps = p.steps
        assert steps[0].__class__ == Feature
        step = steps[1]
        assert step.__class__ == Comment
        self.assertEqual(step.keyword, '#')

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
        self.assertEqual(step_0.keyword, self.scenario_keyword)
        self.assertEqual(step_0.predicate, 'See all vendors')
        self.assertEqual(step_1.keyword, self.given_keyword)
        self.assertEqual(step_1.predicate, 'I am logged in as a user in the administrator role')
        self.assertEqual(step_2.keyword, self.and_keyword)
        self.assertEqual(step_2.predicate, 'There are 3 vendors')
        self.assertEqual(step_3.keyword, self.when_keyword)
        self.assertEqual(step_3.predicate, 'I go to the manage vendors page')
        self.assertEqual(step_4.keyword, self.then_keyword)
        self.assertEqual(step_4.predicate, 'I should see the first 3 vendor names')

    def test_strip_predicates(self):
        language = self._get_language()
        step = Parser(language=language).parse_feature('  %s   gangsta girl   \t     ' % self.given_keyword)[0]
        self.assertEqual(step.keyword, self.given_keyword)
        self.assertEqual(step.predicate, 'gangsta girl')

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

# ####  row zone  #################################

    def test_Row_parse(self):
        sauce = 'buddha | brot |'
        row = Row('#', sauce)
        assert row.predicate == sauce

    def test_parse_feature_Row(self):
        language = self._get_language()
        p = Parser(language=language)
        p.parse_feature(''' | piggy | op |''')
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
        matcher = RegexpStepMatcher(self).add_matcher(MethodNameStepMatcher(self))
        visitor = TestVisitor(self, matcher, NullFormatter())
        global crunks, zones
        crunks = []
        zones = []
        scenario.row_indices = [1, 0, 2]
        scenario.accept(visitor)
        self.assertEqual('hotel', visitor._suite.got_party_zone)
        self.assertEqual('jail', visitor._suite.got_crunk)

    def test_another_two_dimensional_table(self):
        global crunks, zones
        crunks = []
        zones = []
        scene = self.assemble_scene_table_source('Step my milkshake brings all the boys to the yard\n')
        language = self._get_language()
        Parser(language=language).parse_features(scene).evaluate(self)
        self.assertEqual(['work', 'mall', 'jail', 'work', 'mall', 'jail'], crunks)
        self.assertEqual(['beach', 'beach', 'beach', 'hotel', 'hotel', 'hotel'], zones)

    def test_harvest(self):
        r = Row('\|', '')

        def harvest(predicate):
            r.predicate = predicate
            return r.harvest()

        self.assertEqual(['crock', 'of'], harvest('crock | of'))
        self.assertEqual(['crock', 'of'], harvest('crock | of |'))
        self.assertEqual(['crane \| wife', 'three'], harvest('crane \| wife | three'))

    def step_party_zone(self, zone):
        r'party (\w+)'

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

    def test_Rows_find_step_parents(self):
        self.assemble_scene_table()
        given, then, = self.table_scene.steps[0].steps[0].steps
        self.assertEqual(Row, given.steps[0].__class__)
        self.assertEqual(Row, then.steps[0].__class__)
        self.assertEqual('zone  |', given.steps[0].predicate)
        self.assertEqual('crunk |', then.steps[0].predicate)

    def assemble_short_scene_table(self):
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
        self.assertEqual(step.keyword + ': ' + step.predicate, step.reconstruction().strip())

    def step_party_element_from_faction(self, element, faction):
        r'party (\w+) from (\w+)'

        global elements, factions
        factions.append(faction)
        elements.append(element)

    def step_my_milkshake(self, youth='boys', article='the'):
        r'my milkshake brings all the (boys|girls) to (.*) yard'

        self.youth = youth

    def step_exceptional(self):
        x = 1 / 0  # noqa guilty pleasure for programmers!

    def test_handle_exceptions(self):
        s = Step('Given', 'exceptional')
        s.line_number = 42
        matcher = RegexpStepMatcher(self).add_matcher(MethodNameStepMatcher(self))
        visitor = TestVisitor(self, matcher, NullFormatter())
        matcher = self._get_default_machers()

        try:
            visitor.visit(s)
            assert False  # should raise!  # pragma: nocover
        except ZeroDivisionError as e:
            assert 'Given: exceptional' in str(e)

    def test_find_step_by_name(self):
        step = Given(self.given_keyword, 'my milkshake')
        matcher = self._get_default_machers()
        method, args, kwargs = step.find_step(matcher)
        expect = self.step_my_milkshake
        self.assertEqual(expect, method)

    def test_find_step_by_doc_string(self):
        step = And(self.and_keyword, 'my milkshake brings all the boys to the yard')
        matcher = self._get_default_machers()
        method, args, kwargs = step.find_step(matcher)
        expect = self.step_my_milkshake
        self.assertEqual(expect, method)

    def test_find_step_with_match(self):
        step = When(self.when_keyword, 'my milkshake brings all the girls to the yard')
        matcher = self._get_default_machers()
        method, args, kwargs = step.find_step(matcher)
        self.assertEqual(('girls', 'the'), args)

    def test_step_not_found(self):
        step = Then(self.then_keyword, 'not there')
        matcher = self._get_default_machers()
        self.assertRaises(MissingStepError, step.find_step, matcher)

    def step_fail_without_enough_function_name(self):
        step = And(self.and_keyword, 'my milk')
        matcher = self._get_default_machers()
        self.assertRaises(MissingStepError, step.find_step, matcher)

    def step_fail_step_without_enough_doc_string(self):
        step = Given(self.given_keyword, "brings all the boys to the yard it's better than yours")
        matcher = self._get_default_machers()
        self.assertRaises(MissingStepError, step.find_step, matcher)

    def step_evaluate_step_by_doc_string(self):
        step = Given(self.given_keyword, 'my milkshake brings all the girls to a yard')
        self.youth = 'boys'
        matcher = self._get_default_machers()
        visitor = TestVisitor(self, matcher, NullFormatter())
        visitor.visit(step)
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
        matcher = self._get_default_machers()
        visitor = TestVisitor(self, matcher, NullFormatter())
        visitor.visit(steps[0])

    def test_record_filename(self):
        language = self._get_language()
        filename = pwd + '/features/morelia%s.feature' % (language or '')
        thang = Parser(language=language).parse_file(filename)
        feature = thang.steps[0]
        assert feature.__class__ == Feature
        assert feature.filename == filename
        step = feature.steps[3].steps[1]
        assert filename == step.get_filename()

    def test_format_faults_like_python_errors(self):
        language = self._get_language()
        filename = pwd + '/features/morelia%s.feature' % (language or '')
        thang = Parser(language=language).parse_file(filename)
        step = thang.steps[0].steps[3].steps[1]
        assert filename == step.get_filename()
        omen = 'The Alpine glaciers move'
        diagnostic = step.format_fault(omen)
        parent_reconstruction = step.parent.reconstruction().strip('\n')
        reconstruction = step.reconstruction()

        expect = '\n  File "%s", line %s, in %s\n %s\n%s' % \
            (step.get_filename(), step.line_number, parent_reconstruction, reconstruction, omen)

        assert expect == diagnostic

    def test_evaluate_file(self):
        language = self._get_language()
        thang = Parser(language=language).parse_file(pwd + '/features/morelia%s.feature' % (language or ''))
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
        self.keyword = self.step.keyword

    def step_Morelia_evaluates_this(self):
        pass

    def step_culture_contains(self, arguments):
        r'"culture" contains (.*)'

        self.assertEqual(1, arguments.count(self.culture[0]))
        self.assertEqual(1, len(self.culture))

    def step_a_feature_file_with_contents(self, file_contents):
        r'a feature file with "([^"]+)"'
        self.file_contents = file_contents

    def step_Morelia_evaluates_the_file(self):
        self.diagnostic = None

        try:
            language = self._get_language()
            p = Parser(language=language)
            self.file_contents.replace('\\#', '#')  # note - this is how to unescape characters - DIY
            prefix = u'{}: Sample\n{}: Sample\n'.format(self.feature_keyword, self.scenario_keyword)
            p.parse_features(prefix + self.file_contents).evaluate(self)
        except (MissingStepError, AssertionError) as e:
            self.diagnostic = str(e)

    def step_it_prints_a_diagnostic(self, sample):
        r'it prints a diagnostic containing "([^"]+)"'

        self.assert_regex_contains(re.escape(sample), self.diagnostic)

    def step_the_second_line_contains(self, docstring):
        r'the second line contains "([^"]+)"'

        self.assert_regex_contains(re.escape(docstring), self.diagnostic)

    def step_the_step_keyword_is_(self, keyword):
        r'the step keyword is (.+)'

        self.assertEqual(keyword, self.keyword)

    def step_a_source_file_with_a_Given_(self, predicate):
        r'a source file with a (.+)'

        self.predicate = predicate.replace('\\n', '\n')

    def step_we_evaluate_the_file(self):
        r'we evaluate the file'

        matcher = self._get_default_machers()
        self.suggestion, self.extra_arguments = matcher._suggest_doc_string(self.predicate)

    def step_we_convert_it_into_a_(self, suggestion):
        r'we convert it into a (.+)'

        self.assertEqual(suggestion, self.suggestion)

    def step_add_extra_arguments(self, extra=''):
        r'add (.+) arguments'

        self.assertEqual(extra, self.extra_arguments)

    def step_a_file_contains_statements_produce_diagnostics_(self, statements, diagnostics):
        r'a file contains (.+), it produces (.+)'

        try:
            statements = statements.replace('\\n', '\n')
            statements = statements.replace('\\', '')
            language = self._get_language()
            p = Parser(language=language).parse_features(statements)
            p.evaluate(self)
            raise Exception('we expect syntax errors here')  # pragma: nocover
        except (SyntaxError, AssertionError) as e:
            e = e.args[0]
            self.assert_regex_contains(re.escape(diagnostics), e)

    def step_errors(self):
        raise SyntaxError('no, you!')

    def assert_regex_contains(self, pattern, string, flags=None):
        flags = flags or 0
        pattern = to_unicode(pattern)
        string = to_unicode(string)
        diagnostic = u'"%s" not found in "%s"' % (pattern, string)
        self.assertTrue(re.search(pattern, string, flags) is not None, diagnostic)

    def _get_default_machers(self):
        docstring_matcher = RegexpStepMatcher(self)
        method_name_matcher = MethodNameStepMatcher(self)
        docstring_matcher.add_matcher(method_name_matcher)
        return docstring_matcher


@tags(['acceptance'])
class PLMoreliaSuite(MoreliaSuite):

    def setUp(self):
        self.culture = []
        self.feature_keyword = u'Właściwość'
        self.scenario_keyword = u'Scenariusz'
        self.given_keyword = u'Zakładając, że'
        self.then_keyword = u'Wtedy'
        self.when_keyword = u'Gdy'
        self.and_keyword = u'I'

    def _get_language(self):
        return 'pl'

    def test_language_directive(self):
        input = '# language: pl\n%s: prevent wild animals from eating us' % self.feature_keyword
        steps = Parser().parse_feature(input)
        step = steps[0]
        assert step.__class__ == Feature
        self.assertEqual(step.keyword, self.feature_keyword)
        self.assertEqual(step.predicate, 'prevent wild animals from eating us')
