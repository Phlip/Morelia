# -*- coding: utf-8 -*-
#            __  __                _ _
#           |  \/  | ___  _ __ ___| (_) __ _
#           | |\/| |/ _ \| '__/ _ \ | |/ _` |
#           | |  | | (_) | | |  __/ | | (_| |
#           |_|  |_|\___/|_|  \___|_|_|\__,_|
#                             o        o     |  o
#                                 ,_       __|      ,
#                        |  |_|  /  |  |  /  |  |  / \_
#                         \/  |_/   |_/|_/\_/|_/|_/ \/
import itertools
import re
from abc import ABCMeta

from six import moves

from .exceptions import MissingStepError
from .i18n import TRANSLATIONS
from .formatters import NullFormatter
from .matchers import MethodNameStepMatcher, RegexpStepMatcher, ParseStepMatcher
from .utils import to_unicode, fix_exception_encoding
from .visitors import TestVisitor, ReportVisitor, StepMatcherVisitor


__version__ = '0.3.0'


#  TODO  what happens with blank table items?
#  ERGO  river is to riparian as pond is to ___?

LANGUAGE_RE = re.compile(r'^# language: (\w+)')
DEFAULT_LANGUAGE = 'en'


class INode(object):

    __metaclass__ = ABCMeta

    def test_step(self, suite, matcher):
        pass

    def find_step(self, suite, matcher):
        pass


class Morelia(INode):

    def __init__(self, language=DEFAULT_LANGUAGE):
        self.parent = None
        self.language = language
        self.additional_data = {}

    def is_executable(self):
        return False

    def _parse(self, predicate, keyword=None, list=[], line_number=0):
        self.predicate = predicate
        self.keyword = keyword if keyword is not None else str(self)
        self.steps = []
        self.line_number = line_number

#  TODO  escape the sample regices already!
#  and the default code should be 'print <arg_names, ... >'

        for s in list[::-1]:
            mpt = self.my_parent_type()

            try:
                if issubclass(s.__class__, mpt):
                    s.steps.append(self)  # TODO  squeek if can't find parent
                    self.parent = s
                    break
            except TypeError:
                self.enforce(False, 'Only one Feature per file')  # CONSIDER  prevent it don't trap it!!!

        return self

    def prefix(self):
        return ''

    def my_parent_type(self):
        return None

    def _my_regex(self):
        # TODO  calculate name inside
        name = self.i_look_like()
        return r'\s*(' + name + '):?\s+(.*)'

    def evaluate_steps(self, visitor):
        visitor.visit(self)
        for step in self.steps:
            step.evaluate_steps(visitor)

    def i_look_like(self):
        class_name = str(self)
        name = class_name.lower()
        return TRANSLATIONS[self.language].get(name, class_name)

    def count_dimensions(self):
        ''' Get number of rows. '''
        return sum([step.count_dimension() for step in self.steps])

    def count_dimension(self):  # CONSIDER  beautify this crud!
        return 0

    def validate_predicate(self):
        return  # looks good! (-:

    def enforce(self, condition, diagnostic):
        if not condition:
            text = ''
            offset = 1
            if self.parent:
                text = self.parent.reconstruction()
                offset = 5
            text += self.reconstruction()
            text = text.replace('\n\n', '\n').replace('\n', '\n\t')
            raise SyntaxError(diagnostic, (self.get_filename(), self.line_number, offset, text))

    def format_fault(self, diagnostic):
        parent_reconstruction = ''
        if self.parent:
            parent_reconstruction = self.parent.reconstruction().strip('\n')
        reconstruction = self.reconstruction()
        args = (self.get_filename(), self.line_number, parent_reconstruction, reconstruction, diagnostic)
        args = tuple([to_unicode(i) for i in args])
        return u'\n  File "%s", line %s, in %s\n %s\n%s' % args

    def reconstruction(self):
        predicate = self.predicate
        try:
            predicate = predicate.decode('utf-8')
        except (UnicodeDecodeError, UnicodeEncodeError, AttributeError):
            pass
        recon = u'%s%s: %s' % (self.prefix(), self.keyword, predicate)
        if recon[-1] != u'\n':
            recon += u'\n'
        return recon

    def get_real_reconstruction(self, suite, macher):
        return self.reconstruction() + '\n'

    def get_filename(self):
        node = self

        while node:
            if not node.parent and hasattr(node, 'filename'):
                return node.filename
            node = node.parent

        return None


class Parser:
    def __init__(self, language=None):
        self.thangs = [
            Feature, Scenario,
            Given, When, Then, And, But,
            Row, Comment, Step
        ]
        self.steps = []
        self.language = DEFAULT_LANGUAGE if language is None else language

    def parse_file(self, filename):
        prose = open(filename, 'r').read()
        try:
            prose = prose.decode('utf-8')
        except (UnicodeEncodeError, AttributeError):
            pass
        self.parse_features(prose)
        self.steps[0].filename = filename
        return self

    def parse_features(self, prose):
        self.parse_feature(prose)
        return self

    def _create_matcher(self, suite, matcher_classes):
        root_matcher = None
        for matcher_class in matcher_classes:
            matcher = matcher_class(suite)
            if root_matcher is not None:
                root_matcher.add_matcher(matcher)
            else:
                root_matcher = matcher
        return root_matcher

    def evaluate(self, suite, matchers=None, formatter=None, show_all_missing=False):
        if matchers is None:
            matchers = [RegexpStepMatcher, ParseStepMatcher, MethodNameStepMatcher]
        matcher = self._create_matcher(suite, matchers)
        if show_all_missing:
            step_matcher_visitor = StepMatcherVisitor(suite, matcher)
            self.rip(step_matcher_visitor)
        if formatter is None:
            formatter = NullFormatter()
        test_visitor = TestVisitor(suite, matcher, formatter)
        try:
            self.rip(test_visitor)
        except SyntaxError as exc:
            raise
        except Exception as exc:
            fix_exception_encoding(exc)
            raise

    def report(self, suite, visitor_class=ReportVisitor):
        rv = visitor_class(suite)
        self.rip(rv)
        return rv

    def rip(self, visitor):
        if self.steps != []:
            node = self.steps[0]
            visitor.before_feature(node)
            try:
                node.evaluate_steps(visitor)
            finally:
                visitor.after_feature(node)

    def parse_language_directive(self, line):
        """ Parse language directive.

        :param str line: line to parse
        :returns: True if line contains correct language directive
        :side effects: sets self.language to parsed language
        """
        match = LANGUAGE_RE.match(line)
        if match:
            self.language = match.groups()[0]
            return True
        return False

    def parse_feature(self, lines):
        lines = to_unicode(lines)
        self.line_number = 0

        for self.line in lines.split(u'\n'):
            self.line_number += 1

            if self.parse_language_directive(self.line):
                continue

            if not self.line or self.line.startswith('#'):
                continue

            if not self.anneal_last_broken_line() and not self._parse_line():
                if 0 < len(self.steps):
                    self._append_to_previous_node()
                else:
                    s = Step()
                    s.keyword = '???'
                    s.predicate = self.line
                    s.line_number = self.line_number
                    feature_name = TRANSLATIONS[self.language].get('feature', u'Feature')
                    feature_name = feature_name.replace('|', ' or ')
                    s.enforce(False, u'feature files must start with a %s' % feature_name)

        return self.steps

    def anneal_last_broken_line(self):
        if self.steps == []:
            return False  # CONSIDER  no need me
        last_line = self.last_node.predicate

        if re.search(r'\\\s*$', last_line):
            last = self.last_node
            last.predicate += '\n' + self.line
            return True

        return False

#  TODO  permit line breakers in comments
#    | Given a table with one row
#        \| i \| be \| a \| lonely \| row |  table with only one row, line 1

    def _parse_line(self):
        self.line = self.line.rstrip()

        for klass in self.thangs:
            self.thang = klass(language=self.language)
            rx = self.thang._my_regex()
            m = re.compile(rx).match(self.line)

            if m and len(m.groups()) > 0:
                return self._register_line(m.groups())

    def _register_line(self, groups):
        predicate = ''
        if len(groups) > 1:
            predicate = groups[1]
        keyword = groups[0]
        node = self.thang
        node._parse(predicate, keyword, self.steps, self.line_number)
        self.steps.append(node)
        self.last_node = node
        return node

    def _append_to_previous_node(self):
        previous = self.steps[-1]
        previous.predicate += '\n' + self.line.strip()
        previous.predicate = previous.predicate.strip()
        previous.validate_predicate()


class Feature(Morelia):

    def __str__(self):
        return u'Feature'

    def my_parent_type(self):
        return None

    def test_step(self, suite, matcher):
        self.enforce(0 < len(self.steps), 'Feature without Scenario(s)')

    def to_html(self):
        return ['''\n<div><table>
                <tr style="background-color: #aaffbb;" width="100%%">
                <td align="right" valign="top" width="100"><em>%s</em>:</td>
                <td colspan="101">%s</td>
                </tr></table></div>''' % (self.keyword, _clean_html(self.predicate)), '']


class Scenario(Morelia):

    def __str__(self):
        return u'Scenario'

    def my_parent_type(self):
        return Feature

    def evaluate_steps(self, visitor):
        step_schedule = visitor.step_schedule(self)  # TODO  test this permuter directly (and rename it already)

        for step_indices in step_schedule:   # TODO  think of a way to TDD this C-:
            schedule = visitor.permute_schedule(self)

            for indices in schedule:
                self.row_indices = indices
                self.evaluate_test_case(visitor, step_indices)  # note this works on reports too!

    def evaluate_test_case(self, visitor, step_indices):  # note this permutes reports too!
        self.enforce(0 < len(self.steps), 'Scenario without step(s) - Step, Given, When, Then, And, or #')

        visitor.before_scenario(self)
        try:
            self.result = visitor.visit(self)

            for idx, step in enumerate(self.steps):
                if idx in step_indices:
                    step.evaluate_steps(visitor)
        finally:
            visitor.after_scenario(self)

    def permute_schedule(self):  # TODO  rename to permute_row_schedule
        dims = self.count_Row_dimensions()
        return _permute_indices(dims)

    def step_schedule(self):  # TODO  rename to permute_step_schedule !
        sched = []
        pre_slug = []

        #  TODO   deal with steps w/o whens

        for idx, s in enumerate(self.steps):
            if s.__class__ == When:
                break
            else:
                pre_slug.append(idx)

        for idx, s in enumerate(self.steps):
            if s.__class__ == When:
                slug = pre_slug[:]
                slug.append(idx)

                for idx in range(idx + 1, len(self.steps)):
                    s = self.steps[idx]
                    if s.__class__ == When:
                        break
                    slug.append(idx)

                sched.append(slug)

        if sched == []:
            return [pre_slug]
        return sched

    def count_Row_dimensions(self):
        return [step.count_dimensions() for step in self.steps]

    def reconstruction(self):
        return '\n' + self.keyword + ': ' + self.predicate

    def to_html(self):
        return ['''\n<div><table width="100%%">
                <tr style="background-color: #cdffb8;">
                <td align="right" valign="top" width="100"><em>%s</em>:</td>
                <td colspan="101">%s</td></tr>''' % (self.keyword, _clean_html(self.predicate)),
                '</table></div>']


class Step(Morelia):

    def prefix(self):
        return '  '

    def is_executable(self):
        return True

    def __str__(self):
        return u'Step'

    def my_parent_type(self):
        return Scenario

    def find_step(self, suite, matcher):
        predicate = self.predicate
        augmented_predicate = self._augment_predicate()
        method, args, kwargs = matcher.find(predicate, augmented_predicate)
        if method:
            return method, args, kwargs

        suggest, method_name, docstring = matcher.suggest(predicate)
        raise MissingStepError(predicate, suggest, method_name, docstring)

    def get_real_reconstruction(self, suite, matcher):
        predicate = self._augment_predicate()
        try:
            predicate = predicate.decode('utf-8')
        except (UnicodeDecodeError, UnicodeEncodeError, AttributeError):
            pass
        recon = u'%s%s %s' % (self.prefix(), self.keyword, predicate)
        if recon[-1] != u'\n':
            recon += u'\n'
        return recon

    def _augment_predicate(self):  # CONSIDER  unsucktacularize me pleeeeeeze
        if self.parent is None:
            return self.predicate
        dims = self.parent.count_Row_dimensions()
        if set(dims) == set([0]):
            return self.predicate
        rep = re.compile(r'\<(\w+)\>')
        replitrons = rep.findall(self.predicate)
        if replitrons == []:
            return self.predicate
        self.copy = self.predicate[:]
        row_indices = self.parent.row_indices

        for self.replitron in replitrons:
            for x in range(0, len(row_indices)):
                self.table = self.parent.steps[x].steps

                if self.table != []:
                    q = 0

                    for self.title in self.table[0].harvest():
                        self.replace_replitron(x, q, row_indices)
                        q += 1

        return self.copy

    def evaluate(self, suite, matcher):
        method, args, kwargs = self.find_step(suite, matcher)
        method(*args, **kwargs)

    def test_step(self, suite, matcher):
        try:
            self.evaluate(suite, matcher)
        except MissingStepError as exc:
            message = self.format_fault(exc.suggest)
            exc.args = (message,)
            raise
        except Exception as exc:
            message = self.format_fault(exc.args[0])
            exc.args = (message,) + exc.args[1:]
            raise

    def replace_replitron(self, x, q, row_indices):
        if self.title != self.replitron:
            return
        at = row_indices[x] + 1

        if at >= len(self.table):
            print('CONSIDER this should never happen')
            return

        #  CONSIDER  we hit this too many times - hit once and stash the result
        #  CONSIDER  better diagnostics when we miss these

        stick = self.table[at].harvest()
        found = stick[q]  # CONSIDER  this array overrun is what you get when your table is ragged
        # CONSIDER  only if it's not nothing?
        found = found.replace('\n', '\\n')  # CONSIDER  crack the multi-line argument bug, and take this hack out!
        self.copy = self.copy.replace('<%s>' % self.replitron, found)

        # CONSIDER  mix replitrons and matchers!

    def to_html(self):
        return '\n<tr><td align="right" valign="top"><em>' + self.keyword + '</em></td><td colspan="101">' + _clean_html(self.predicate) + '</td></tr>', ''


class Given(Step):  # CONSIDER  distinguish these by fault signatures!

    def __str__(self):
        return u'Given'

    def prefix(self):
        return '  '


class When(Step):  # TODO  cycle these against the Scenario

    def __str__(self):
        return u'When'

    def prefix(self):
        return '   '

    def to_html(self):
        return '\n<tr style="background-color: #cdffb8; background: url(http://www.zeroplayer.com/images/stuff/aqua_gradient.png) no-repeat; background-size: 100%;"><td align="right" valign="top"><em>' + self.keyword + '</em></td><td colspan="101">' + _clean_html(self.predicate) + '</td></tr>', ''


class Then(Step):

    def __str__(self):
        return u'Then'

    def prefix(self):
        return '   '


class And(Step):

    def __str__(self):
        return u'And'

    def prefix(self):
        return '    '


class But(And):

    def __str__(self):
        return u'But'

#  CONSIDER  how to validate that every row you think you wrote actually ran?


class Row(Morelia):

    def __str__(self):
        return u'Row'

    def i_look_like(self):
        return r'\|'

    def my_parent_type(self):
        return Step

    def prefix(self):
        return '        '

    def reconstruction(self):  # TODO  strip the reconstruction at error time
        recon = self.prefix() + '| ' + self.predicate
        if recon[-1] != '\n':
            recon += '\n'
        return recon

    def to_html(self):
        html = '\n<tr><td></td>'
        idx = self.parent.steps.index(self)
        em = 'span'
        if idx == 0:
            color = 'silver'
            em = 'em'
        elif ((2 + idx) / 3) % 2 == 0:
            color = '#eeffff'
        else:
            color = '#ffffee'

        for col in self.harvest():
            html += '<td style="background-color: %s;"><%s>' % (color, em) + _clean_html(col) + '</%s></td>' % em

        html += '<td>&#160;</td></tr>'  # CONSIDER  the table needn't stretch out so!
        return html, ''

    def count_dimension(self):
        if self is self.parent.steps[0]:
            # header row
            return 0
        return 1  # TODO  raise an error (if the table has one row!)

    def harvest(self):
        row = re.split(r' \|', re.sub(r'\|$', '', self.predicate))
        row = [s.strip() for s in row]
        return row

#  TODO  sample data with "post-it haiku"
#  CONSIDER  trailing comments


class Comment(Morelia):

    def __str__(self):
        return u'Comment'

    def i_look_like(self):
        return r'\#'

    def my_parent_type(self):
        return Morelia  # aka "any"

    def _my_regex(self):
        name = self.i_look_like()
        return r'\s*(' + name + ')(.*)'

    def validate_predicate(self):
        self.enforce(self.predicate.count('\n') == 0, 'linefeed in comment')

    def reconstruction(self):
        recon = '  # ' + self.predicate
        if recon[-1] != '\n':
            recon += '\n'
        return recon

    def to_html(self):
        return '\n# <em>' + _clean_html(self.predicate) + '</em><br/>', ''


def _special_range(n):  # CONSIDER  better name
    return moves.range(n) if n else [0]


def _permute_indices(arr):
    product_args = list(_imap(arr))
    result = list(itertools.product(*product_args))
    return result
    #  tx to Chris Rebert, et al, on the Python newsgroup for curing my brainlock here!!


def _imap(*iterables):
    iterables = [iter(i) for i in iterables]
    while True:
        args = [next(i) for i in iterables]
        yield _special_range(*args)


def _clean_html(string):
    return string.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')
