from abc import ABCMeta, abstractmethod
from collections import OrderedDict
import time

from .exceptions import MissingStepError


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

    def __init__(self, suite, matcher):
        self._suite = suite
        self._matcher = matcher

    def visit(self, node):
        self._suite.step = node
        start_time = time.time()
        status = ''
        try:
            try:
                node.test_step(self._suite, self._matcher)
            except (MissingStepError, AssertionError):
                status = 'Fail'
                raise
            except Exception:
                status = 'Error'
                raise
            else:
                status = 'OK'
        finally:
            end_time = time.time()
            additional_data = node.additional_data
            additional_data['duration'] = end_time - start_time
            additional_data['status'] = status

    def before_scenario(self, node):
        self._suite.setUp()

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
            self._not_matched[e.suggest] = True

    def after_feature(self, node):
        suggest = u''.join(self._not_matched.keys())
        if suggest:
            diagnostic = u'Cannot match steps:\n\n%s' % suggest
            self._suite.fail(diagnostic)
#
#
# class TextReportVisitor(IVisitor):
#     def __init__(self, suite, matcher):
#         self._suite = suite
#         self._result = ''
#
#     def visit(self, node):
#         duration = node.additional_data.get('duration', 0)
#         if duration:
#             duration = '#  %.6fs' % duration
#         else:
#             duration = ''
#         self._result += '%-57s %s\n' % (
#             node.reconstruction().strip('\n'),
#             duration,
#         )
#
#     def __str__(self):
#         return self._result
#
#     def __unicode__(self):
#         return unicode(self._result)
