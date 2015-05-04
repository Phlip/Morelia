from abc import ABCMeta, abstractmethod
from collections import OrderedDict
import time

from .exceptions import MissingStepError
from .utils import to_docstring


class IVisitor(object):

    __metaclass__ = ABCMeta

    def before_feature(self, node):
        pass

    def after_feature(self, node):
        pass

    def before_scenario(self, node):
        pass

    def after_scenario(self, node):
        pass

    def permute_schedule(self, node):
        return [[0]]

    def step_schedule(self, node):
        return [list(range(len(node.steps)))]

    @abstractmethod
    def visit(self):
        pass  # pragma: nocover


class TestVisitor(IVisitor):
    """ Visits all steps and run step methods. """

    def __init__(self, suite, matcher, formatter):
        self._suite = suite
        self._matcher = matcher
        self._formatter = formatter
        self._scenarios_num = 0
        self._steps_num = 0

    def visit(self, node):
        self._suite.step = node
        self._steps_num += 1
        line = node.get_real_reconstruction(self._suite, self._matcher)
        start_time = time.time()
        try:
            try:
                node.test_step(self._suite, self._matcher)
            except (MissingStepError, AssertionError):
                status = 'fail'
                raise
            except (SystemExit, Exception):
                status = 'error'
                raise
            else:
                status = 'pass'
        finally:
            end_time = time.time()
            duration = end_time - start_time
            self._formatter.output(node, line, status, duration)

    def before_scenario(self, node):
        self._suite.setUp()
        self._scenarios_num += 1

    def after_scenario(self, node):
        self._suite.tearDown()

    def permute_schedule(self, node):
        return node.permute_schedule()

    def step_schedule(self, node):
        return node.step_schedule()


class ReportVisitor(IVisitor):
    def __init__(self, suite):
        self._suite = suite
        self._result = ''

    def visit(self, node):
        recon, result = node.to_html()
        if recon[-1] != '\n':
            recon += '\n'  # TODO  clean this outa def reconstruction(s)!
        self._result += recon
        return result

    def after_scenario(self, node):
        if node.result:
            self._result += node.result

    def __str__(self):
        return self._result

    def __unicode__(self):
        return unicode(self._result)


class StepMatcherVisitor(IVisitor):
    """ Visits all steps in order to find missing step methods. """

    def __init__(self, suite, matcher):
        self._suite = suite
        self._not_matched = OrderedDict()
        self._matcher = matcher

    def visit(self, node):
        try:
            node.find_step(self._suite, self._matcher)
        except MissingStepError as e:
            if e.docstring:
                self._not_matched[e.docstring] = e.suggest
            else:
                self._not_matched[e.method_name] = e.suggest

    def after_feature(self, node):
        suggest = u''.join(self._not_matched.values())
        if suggest:
            diagnostic = u'Cannot match steps:\n\n%s' % suggest
            self._suite.fail(to_docstring(diagnostic))
