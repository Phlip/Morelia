import inspect
import sys
import traceback
from gettext import ngettext
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
import time

from .grammar import Feature, Scenario, Step
from .exceptions import MissingStepError
from .utils import to_docstring, fix_exception_encoding, to_unicode


class IVisitor(object):

    __metaclass__ = ABCMeta

    def permute_schedule(self, node):
        return [[0]]

    @abstractmethod
    def visit(self, node):
        pass  # pragma: nocover

    @abstractmethod
    def after_visit(self, node):
        pass  # pragma: nocover


def noop():
    pass


class TestVisitor(IVisitor):
    """ Visits all steps and run step methods. """

    def __init__(self, suite, matcher, formatter):
        self._setUp = suite.setUp
        self._tearDown = suite.tearDown
        self._suite = suite
        self._suite.setUp = self._suite.tearDown = noop
        self._matcher = matcher
        self._formatter = formatter
        self._exceptions = []
        self._scenarios_failed = 0
        self._scenarios_passed = 0
        self._scenarios_num = 0
        self._scenario_exception = None
        self._steps_num = 0

    def visit(self, node):
        # no support for single dispatch for methods in python yet
        if isinstance(node, Feature):
            self._feature_visit(node)
        elif isinstance(node, Scenario):
            self._scenario_visit(node)
        elif isinstance(node, Step):
            self._step_visit(node)
        else:
            line = node.get_real_reconstruction()
            self._formatter.output(node, line, '', 0)

    def after_visit(self, node):
        if isinstance(node, Feature):
            self._feature_after_visit(node)
        elif isinstance(node, Scenario):
            self._scenario_after_visit(node)

    def _feature_visit(self, node):
        self._exceptions = []
        self._scenarios_failed = 0
        self._scenarios_passed = 0
        self._scenarios_num = 0
        line = node.get_real_reconstruction()
        self._formatter.output(node, line, '', 0)

    def _feature_after_visit(self, node):
        if self._scenarios_failed:
            self._fail_feature()

    def _fail_feature(self):
        failed_msg = ngettext('{} scenario failed', '{} scenarios failed', self._scenarios_failed)
        passed_msg = ngettext('{} scenario passed', '{} scenarios passed', self._scenarios_passed)
        msg = u'{}, {}'.format(failed_msg, passed_msg).format(self._scenarios_failed, self._scenarios_passed)
        prefix = '-' * 66
        for step_line, tb, exc in self._exceptions:
            msg += u'\n{}{}\n{}{}'.format(prefix, step_line, tb, exc).replace(u'\n', u'\n    ')
        assert self._scenarios_failed == 0, msg

    def _scenario_visit(self, node):
        self._scenario_exception = None
        if self._scenarios_num != 0:
            self._setUp()
        self._scenarios_num += 1
        line = node.get_real_reconstruction()
        self._formatter.output(node, line, '', 0)

    def _scenario_after_visit(self, node):
        if self._scenario_exception:
            self._exceptions.append(self._scenario_exception)
            self._scenarios_failed += 1
        else:
            self._scenarios_passed += 1
        self._tearDown()

    def _step_visit(self, node):
        if self._scenario_exception:
            return
        self._suite.step = node
        self._steps_num += 1
        reconstruction = node.get_real_reconstruction()
        start_time = time.time()
        status = 'pass'
        try:
            self.run_step(node)
        except (MissingStepError, AssertionError) as exc:
            status = 'fail'
            etype, evalue, etraceback = sys.exc_info()
            tb = traceback.extract_tb(etraceback)[:-2]
            fix_exception_encoding(evalue)
            self._scenario_exception = (
                node.parent.get_real_reconstruction() + reconstruction,
                ''.join(to_unicode(line) for line in traceback.format_list(tb)),
                ''.join(to_unicode(line) for line in traceback.format_exception_only(etype, evalue))
            )
        except (SystemExit, Exception) as exc:
            status = 'error'
            self._format_exception(node, exc)
            raise
        finally:
            end_time = time.time()
            duration = end_time - start_time
            self._formatter.output(node, reconstruction, status, duration)

    def _format_exception(self, node, exc):
        if len(exc.args):
            message = node.format_fault(exc.args[0])
            exc.args = (message,) + exc.args[1:]

    def run_step(self, node):
        method, args, kwargs = node.find_step(self._matcher)
        spec = inspect.getargspec(method)
        if '_labels' in spec.args or spec.keywords:
            kwargs['_labels'] = node.get_labels()
        if '_text' in spec.args or spec.keywords:
            kwargs['_text'] = node.payload
        method(*args, **kwargs)

    def permute_schedule(self, node):
        return node.permute_schedule()


class StepMatcherVisitor(IVisitor):
    """ Visits all steps in order to find missing step methods. """

    def __init__(self, suite, matcher):
        self._suite = suite
        self._not_matched = OrderedDict()
        self._matcher = matcher

    def visit(self, node):
        try:
            node.find_step(self._matcher)
        except MissingStepError as e:
            if e.docstring:
                self._not_matched[e.docstring] = e.suggest
            else:
                self._not_matched[e.method_name] = e.suggest

    def after_visit(self, node):
        pass

    def report_missing(self):
        suggest = u''.join(self._not_matched.values())
        if suggest:
            diagnostic = u'Cannot match steps:\n\n{}'.format(suggest)
            self._suite.fail(to_docstring(diagnostic))
