from abc import ABCMeta, abstractmethod
import re


class IStepMatcher(object):
    """ Matches methods to steps.

    Chain of Responsibility.
    """

    __metaclass__ = ABCMeta

    def __init__(self, suite, step_pattern='^step_'):
        self._suite = suite
        self._matcher = re.compile(step_pattern)
        self._next = None

    def _get_all_step_methods(self):
        match = self._matcher.match
        return [method_name for method_name in dir(self._suite) if match(method_name)]

    def add_matcher(self, matcher):
        """ Add new matcher at end of CoR

        :param matcher: matcher to add
        :returns: self
        """
        if self._next is None:
            self._next = matcher
        else:
            self._next.add_matcher(matcher)
        return self

    def find(self, predicate, augmented_predicate, step_methods=None):
        if step_methods is None:
            step_methods = self._get_all_step_methods()
        method, matches = self.match(predicate, augmented_predicate, step_methods)
        if method:
            return method, matches
        if self._next is not None:
            return self._next.find(predicate, augmented_predicate, step_methods)
        return None, []

    @abstractmethod
    def match(self, predicate, augmented_predicate, step_methods):
        pass  # pragma: nocover


class ByNameStepMatcher(IStepMatcher):

    def match(self, predicate, augmented_predicate, step_methods):
        clean = re.sub(r'[^\w]', '_?', predicate)
        pattern = '^step_' + clean + '$'
        regexp = re.compile(pattern)
        step_methods = [method for method in step_methods if regexp.match(method)]
        for method_name in step_methods:
            method = self._suite.__getattribute__(method_name)
            return method, []
        return None, []
