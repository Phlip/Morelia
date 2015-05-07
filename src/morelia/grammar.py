from abc import ABCMeta
import copy
import itertools
import re

from six import moves

from .exceptions import MissingStepError
from .formatters import NullFormatter
from .i18n import TRANSLATIONS
from .matchers import RegexpStepMatcher, ParseStepMatcher, MethodNameStepMatcher
from .utils import fix_exception_encoding, to_unicode
from .visitors import StepMatcherVisitor, TestVisitor, ReportVisitor


class AST(object):

    def __init__(self, steps, test_visitor_class=TestVisitor,
                 matcher_visitor_class=StepMatcherVisitor):
        self.steps = steps
        self._test_visitor_class = test_visitor_class
        self._matcher_visitor_class = matcher_visitor_class

    def evaluate(self, suite, formatter=None, matchers=None, show_all_missing=False):
        if matchers is None:
            matchers = [RegexpStepMatcher, ParseStepMatcher, MethodNameStepMatcher]
        matcher = self._create_matchers_chain(suite, matchers)
        feature = self.steps[0]
        if show_all_missing:
            matcher_visitor = self._matcher_visitor_class(suite, matcher)
            feature.evaluate_steps(matcher_visitor)
        if formatter is None:
            formatter = NullFormatter()
        test_visitor = self._test_visitor_class(suite, matcher, formatter)
        try:
            feature.evaluate_steps(test_visitor)
        except SyntaxError as exc:
            raise
        except Exception as exc:
            fix_exception_encoding(exc)
            raise

    def _create_matchers_chain(self, suite, matcher_classes):
        root_matcher = None
        for matcher_class in matcher_classes:
            matcher = matcher_class(suite)
            try:
                root_matcher.add_matcher(matcher)
            except AttributeError:
                root_matcher = matcher
        return root_matcher

    def report(self, suite, visitor_class=ReportVisitor):
        rv = visitor_class(suite)
        self.steps[0].evaluate_steps(rv)
        return rv


class INode(object):

    __metaclass__ = ABCMeta

    def test_step(self, suite, matcher):
        pass

    def find_step(self, suite, matcher):
        pass

    def evaluate_steps(self, visitor):
        class_name = self.__class__.__name__.lower()
        self._method_hook(visitor, class_name, 'before_')
        try:
            visitor.visit(self)
            self._evaluate_child_steps(visitor)
        finally:
            self._method_hook(visitor, class_name, 'after_')

    def _evaluate_child_steps(self, visitor):
        for step in self.steps:
            step.evaluate_steps(visitor)

    def _method_hook(self, visitor, class_name, prefix):
        method = getattr(visitor, 'after_%s' % class_name, None)
        if method:
            method(self)


class Morelia(INode):

    def __init__(self, keyword, predicate):
        self.parent = None
        self.additional_data = {}
        self.keyword = keyword
        self.predicate = predicate if predicate is not None else ''

    def is_executable(self):
        return False

    def connect_to_parent(self, steps=[], line_number=0):
        self.steps = []
        self.line_number = line_number

#  TODO  escape the sample regices already!
#  and the default code should be 'print <arg_names, ... >'

        mpt = self.my_parent_type()
        try:
            for step in steps[::-1]:
                if isinstance(step, mpt):
                    step.steps.append(self)  # TODO  squeek if can't find parent
                    self.parent = step
                    break
        except TypeError:
            self.enforce(False, 'Only one Feature per file')  # CONSIDER  prevent it don't trap it!!!

        steps.append(self)
        return self

    def prefix(self):
        return ''

    def my_parent_type(self):
        return None

    @classmethod
    def get_pattern(cls, language):
        class_name = cls.__name__
        name = class_name.lower()
        name = TRANSLATIONS[language].get(name, class_name)
        return r'\s*(?P<keyword>' + name + '):?(?:\s+(?P<predicate>.*))?$'

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
        predicate = to_unicode(self.predicate)
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


class Feature(Morelia):

    def test_step(self, suite, matcher):
        self.enforce(0 < len(self.steps), 'Feature without Scenario(s)')

    def to_html(self):
        return ['''\n<div><table>
                <tr style="background-color: #aaffbb;" width="100%%">
                <td align="right" valign="top" width="100"><em>%s</em>:</td>
                <td colspan="101">%s</td>
                </tr></table></div>''' % (self.keyword, _clean_html(self.predicate)), '']

    def prepend_steps(self, scenario):
        background = scenario.parent.steps[0]
        try:
            background.prepend_steps(scenario)
        except AttributeError:
            pass

    def reconstruction(self):
        predicate = to_unicode(self.predicate)
        predicate = predicate.replace('\n', '\n    ')
        recon = u'%s%s: %s' % (self.prefix(), self.keyword, predicate)
        if recon[-1] != u'\n':
            recon += u'\n'
        return recon


class Scenario(Morelia):

    def my_parent_type(self):
        return Feature

    def evaluate_steps(self, visitor):
        if self.parent:
            self.parent.prepend_steps(self)
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


class Background(Morelia):

    def my_parent_type(self):
        return Feature

    def _evaluate_child_steps(self, visitor):
        pass

    def prepend_steps(self, scenario):
        new_steps = []
        for step in self.steps:
            new_step = copy.copy(step)
            new_step.parent = scenario
            new_steps.append(new_step)
        scenario.steps = new_steps + scenario.steps


class Step(Morelia):

    def prefix(self):
        return '  '

    def is_executable(self):
        return True

    def my_parent_type(self):
        return (Scenario, Background)

    def find_step(self, suite, matcher):
        predicate = self.predicate
        augmented_predicate = self._augment_predicate()
        method, args, kwargs = matcher.find(predicate, augmented_predicate)
        if method:
            return method, args, kwargs

        suggest, method_name, docstring = matcher.suggest(predicate)
        raise MissingStepError(predicate, suggest, method_name, docstring)

    def get_real_reconstruction(self, suite, matcher):
        predicate = to_unicode(self._augment_predicate())
        recon = u'    %s %s' % (self.keyword, predicate)
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

        for replitron in replitrons:
            for x in range(0, len(row_indices)):
                table = self.parent.steps[x].steps

                try:
                    row = next(moves.filter(lambda step: isinstance(step, Row), table))
                except StopIteration:
                    pass
                else:
                    for q, title in enumerate(row.harvest()):
                        self.replace_replitron(x, q, row_indices, table, title, replitron)

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
            if len(exc.args):
                message = exc.args[0]
                message = self.format_fault(message)
                exc.args = (message,) + exc.args[1:]
            raise

    def replace_replitron(self, x, q, row_indices, table, title, replitron):
        if title != replitron:
            return
        at = row_indices[x] + 1

        assert at < len(table), 'CONSIDER this should never happen'

        #  CONSIDER  we hit this too many times - hit once and stash the result
        #  CONSIDER  better diagnostics when we miss these

        stick = table[at].harvest()
        found = stick[q]  # CONSIDER  this array overrun is what you get when your table is ragged
        # CONSIDER  only if it's not nothing?
        found = found.replace('\n', '\\n')  # CONSIDER  crack the multi-line argument bug, and take this hack out!
        self.copy = self.copy.replace('<%s>' % replitron, found)

        # CONSIDER  mix replitrons and matchers!

    def to_html(self):
        return '\n<tr><td align="right" valign="top"><em>' + self.keyword + '</em></td><td colspan="101">' + _clean_html(self.predicate) + '</td></tr>', ''


class Given(Step):  # CONSIDER  distinguish these by fault signatures!

    pass


class When(Step):  # TODO  cycle these against the Scenario

    def to_html(self):
        return '\n<tr style="background-color: #cdffb8; background: url(http://www.zeroplayer.com/images/stuff/aqua_gradient.png) no-repeat; background-size: 100%;"><td align="right" valign="top"><em>' + self.keyword + '</em></td><td colspan="101">' + _clean_html(self.predicate) + '</td></tr>', ''


class Then(Step):

    pass


class And(Step):

    pass


class But(And):

    pass

#  CONSIDER  how to validate that every row you think you wrote actually ran?


class Row(Morelia):

    @classmethod
    def get_pattern(cls, language):
        return r'\s*(?P<keyword>\|):?\s+(?P<predicate>.*)'

    def my_parent_type(self):
        return (Step, Examples)

    def prefix(self):
        return ' ' * 8

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


class Examples(Morelia):

    def prefix(self):
        return ' ' * 4

    def my_parent_type(self):
        return Scenario

#  TODO  sample data with "post-it haiku"
#  CONSIDER  trailing comments


class Comment(Morelia):

    def my_parent_type(self):
        return Morelia  # aka "any"

    @classmethod
    def get_pattern(cls, language):
        return r'\s*(?P<keyword>\#)(?P<predicate>.*)'

    def validate_predicate(self):
        self.enforce(self.predicate.count('\n') == 0, 'linefeed in comment')

    def reconstruction(self):
        recon = '    # ' + self.predicate
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
