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

__version__ = '0.2.0'

#  TODO  get working with python 3,4,5, etc...
#  TODO  put http://www.dawnoftimecomics.com/index.php on comixpedia!

import itertools
import re
from six import moves
import unicodedata

from .i18n import TRANSLATIONS
from .utils import to_unicode

#  TODO  what happens with blank table items?
#  ERGO  river is to riparian as pond is to ___?

LANGUAGE_RE = re.compile(r'^# language: (\w+)')
DEFAULT_LANGUAGE = 'en'


class Morelia:

    def __init__(self, language=DEFAULT_LANGUAGE):
        self.parent = None
        self.language = language

    def _parse(self, predicate, list=[], line_number=0):
        self.concept = str(self)
        self.predicate = predicate
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

    def evaluate_steps(self, v):
        v.visit(self)
        for step in self.steps:
            step.evaluate_steps(v)

    def test_step(self, v):
        pass

    def i_look_like(self):
        class_name = str(self)
        name = class_name.lower()
        return TRANSLATIONS[self.language].get(name, class_name)

    def count_dimensions(self):
        return sum([step.count_dimension() for step in self.steps])

    def count_dimension(self):  # CONSIDER  beautify this crud!
        return 0

    def validate_predicate(self):
        return  # looks good! (-:

    def enforce(self, condition, diagnostic):
        if not condition:
            msg = self.format_fault(diagnostic)
            raise SyntaxError(msg)

    def format_fault(self, diagnostic):
        parent_reconstruction = ''
        if self.parent:
            parent_reconstruction = self.parent.reconstruction().replace('\n', '\\n')
        reconstruction = self.reconstruction().replace('\n', '\\n')
        args = (self.get_filename(), self.line_number, parent_reconstruction, reconstruction, diagnostic)
        args = tuple([to_unicode(i) for i in args])
        return u'\n  File "%s", line %s, in %s\n    %s\n%s' % args

    def reconstruction(self):
        predicate = self.predicate
        try:
            predicate = predicate.decode('utf-8')
        except (UnicodeDecodeError, UnicodeEncodeError, AttributeError):
            pass
        recon = u'%s%s: %s' % (self.prefix(), self.concept, predicate)
        if recon[-1] != u'\n':
            recon += u'\n'
        return recon

    def get_filename(self):
        node = self

        while node:
            if not node.parent and hasattr(node, 'filename'):
                return node.filename
            node = node.parent

        return None


class Viridis(Morelia):

    def prefix(self):
        return '  '

    @staticmethod
    def slugify(predicate):
        predicate = unicodedata.normalize('NFD', predicate).encode('ascii', 'replace').decode('utf-8')
        predicate = predicate.replace(u'??', u'_').replace(u'?', u'')
        return re.sub(u'[^\w]+', u'_', predicate, re.U).strip('_')

    def find_step_name(self, suite):
        self.method = None
        self.find_by_doc_string(suite)
        if not self.method:
            self.find_by_name(suite)
        if self.method:
            return self.method_name
        doc_string = self.suggest_doc_string()
        arguments = u'(self%s)' % self.extra_arguments  # note this line ain't tested! C-:
        method_name = 'step_' + self.slugify(self.predicate)

        diagnostic = u'Cannot match step: ' + self.predicate + u'\n' + \
                     u'suggest:\n\n' + \
                     u'    def ' + method_name + arguments + u':\n' + \
                     u'        ' + doc_string + u'\n\n' + \
                     u'        # code\n\n'

        suite.fail(diagnostic)

    def suggest_doc_string(self, predicate=None):  # CONSIDER  invent Ruby scan here, to dazzle the natives
        self.extra_arguments = ''
        if not predicate:
            predicate = self.predicate
        predicate = predicate.replace("'", "\\'")
        predicate = predicate.replace('\n', '\\n')
        self._add_extra_args(r'\<(.+?)\>', predicate)
        predicate = re.sub(r'\<.+?\>', '(.+)', predicate)
        self._add_extra_args(r'"(.+?)"', predicate)
        predicate = re.sub(r'".+?"', '"([^"]+)"', predicate)
        predicate = re.sub(r' \s+', '\\s+', predicate)
        predicate = predicate.replace('\n', '\\n')
        return "ur'" + predicate + "'"

    def _add_extra_args(self, matcher, predicate):
        args = re.findall(matcher, predicate)
        for arg in args:
            self.extra_arguments += ', ' + self.slugify(arg)

    def find_by_name(self, suite):
        self.method_name = None
        clean = re.sub(r'[^\w]', '_?', self.predicate)
        self.matches = []

        for s in self.find_steps(suite, '^step_' + clean + '$'):  # NOTE  the ^$ ain't tested
            self.method_name = s
            self.method = suite.__getattribute__(s)
            return

    def find_by_doc_string(self, suite):
        self.method_name = None

        for s in self.find_steps(suite, '^step_'):
            self.method_name = s
            method = suite.__getattribute__(s)
            doc = method.__doc__

            if doc:
                doc = re.compile('^' + doc + '$')  # CONSIDER deal with users who put in the ^$
                m = doc.match(self.augment_predicate())

                if m:
                    self.matches = m.groups()
                    self.method = method
                    return

    def find_steps(self, suite, regexp):
        matcher = re.compile(regexp)
        list = []

        for s in dir(suite):
            if matcher.match(s):
                list.append(s)

        return list

    def evaluate(self, suite):
        self.find_step_name(suite)
        self.method(*self.matches)


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

    def evaluate(self, suite):
        self.rip(TestVisitor(suite))  # CONSIDER  rename to Viridis

    def report(self, suite):
        rv = ReportVisitor(suite)
        self.rip(rv)
        return rv

    def rip(self, v):
        if self.steps != []:
            self.steps[0].evaluate_steps(v)

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
                    s.concept = '???'
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
        node = self.thang
        node._parse(predicate, self.steps, self.line_number)
        self.steps.append(node)
        self.last_node = node
        return node

    def _append_to_previous_node(self):
        previous = self.steps[-1]
        previous.predicate += '\n' + self.line.strip()
        previous.predicate = previous.predicate.strip()
        previous.validate_predicate()


class ReportVisitor:
    def __init__(self, suite):
        self.suite = suite
    string = ''

    def permute_schedule(self, node):
        return [[0]]

    def step_schedule(self, node):
        return [[x for x in range(len(node.steps))]]

    def visit(self, node):
        recon, we_owe = node.to_html()
        if recon[-1] != '\n':
            recon += '\n'  # TODO  clean this outa def reconstruction(s)!
        self.string += recon
        return we_owe

    def owed(self, owed):
        self.string += owed

    def __str__(self):
        return self.string

    def __unicode__(self):
        return unicode(self.string)


class TestVisitor:

    def __init__(self, suite):
        self.suite = suite

    def permute_schedule(self, node):
        return node.permute_schedule()

    def step_schedule(self, node):
        return node.step_schedule()

    def visit(self, node):
        # print node.reconstruction()  # CONSIDER  if verbose
        self.suite.step = node
        node.test_step(self)

    def owed(self, igme):
        pass


class Feature(Morelia):

    def __str__(self):
        return u'Feature'

    def my_parent_type(self):
        return None

    def test_step(self, v):
        self.enforce(0 < len(self.steps), 'Feature without Scenario(s)')

    def to_html(self):
        return ['''\n<div><table>
                <tr style="background-color: #aaffbb;" width="100%%">
                <td align="right" valign="top" width="100"><em>%s</em>:</td>
                <td colspan="101">%s</td>
                </tr></table></div>''' % (self.concept, _clean_html(self.predicate)), '']


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

    def evaluate_test_case(self, visitor, step_indices=None):  # note this permutes reports too!
        self.enforce(0 < len(self.steps), 'Scenario without step(s) - Step, Given, When, Then, And, or #')

        name = self.steps[0].find_step_name(visitor.suite)
        visitor.suite = visitor.suite.__class__(name)
        # print self.predicate  #  CONSIDER  if verbose
        visitor.suite.setUp()

        try:
            u_owe = visitor.visit(self)

            for idx, step in enumerate(self.steps):
                if step_indices is None or idx in step_indices:  # TODO  take out the default arg
                    step.evaluate_steps(visitor)

            visitor.owed(u_owe)
        finally:
            visitor.suite.tearDown()

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
        return '\n' + self.concept + ': ' + self.predicate

    def to_html(self):
        return ['''\n<div><table width="100%%">
                <tr style="background-color: #cdffb8;">
                <td align="right" valign="top" width="100"><em>%s</em>:</td>
                <td colspan="101">%s</td></tr>''' % (self.concept, _clean_html(self.predicate)),
                '</table></div>']


class Step(Viridis):

    def __str__(self):
        return u'Step'

    def my_parent_type(self):
        return Scenario

    def test_step(self, v):
        self.find_step_name(v.suite)

# ERGO  use "born again pagan" somewhere

        try:
            self.method(*self.matches)
        except (Exception, SyntaxError) as e:
            new_exception = self.format_fault(to_unicode(e))
            e.args = (new_exception,) + (e.args[1:])
            if type(e) == SyntaxError:
                raise SyntaxError(repr(new_exception))
            raise

    def augment_predicate(self):  # CONSIDER  unsucktacularize me pleeeeeeze
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

        for self.replitron in replitrons:
            for x in range(0, len(self.parent.row_indices)):
                self.table = self.parent.steps[x].steps

                if self.table != []:
                    q = 0

                    for self.title in self.table[0].harvest():
                        self.replace_replitron(x, q)
                        q += 1

        return self.copy

    def replace_replitron(self, x, q):
        if self.title != self.replitron:
            return
        at = self.parent.row_indices[x] + 1

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
        return '\n<tr><td align="right" valign="top"><em>' + self.concept + '</em></td><td colspan="101">' + _clean_html(self.predicate) + '</td></tr>', ''


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
        return '\n<tr style="background-color: #cdffb8; background: url(http://www.zeroplayer.com/images/stuff/aqua_gradient.png) no-repeat; background-size: 100%;"><td align="right" valign="top"><em>' + self.concept + '</em></td><td colspan="101">' + _clean_html(self.predicate) + '</td></tr>', ''


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

#  CONSIDER  display all missing steps not just the first
#  ERGO  Morelia should raise a form in any state!
#  ERGO  get Morelia working with more Pythons - virtualenv it!
#  ERGO  moralia should try the regex first then the step name
#  ERGO  pay for "Bartender" by Sacred Hoop


if __name__ == '__main__':
    import os
    os.system('python ../tests/morelia_suite.py')   # NOTE  this might not return the correct shell value
