from .formatters import NullFormatter
from .matchers import RegexpStepMatcher, ParseStepMatcher, MethodNameStepMatcher
from .utils import fix_exception_encoding
from .visitors import StepMatcherVisitor, TestVisitor, ReportVisitor


class AST(object):

    def __init__(self, steps):
        self.steps = steps

    def evaluate(self, suite, matchers=None, formatter=None, show_all_missing=False):
        if matchers is None:
            matchers = [RegexpStepMatcher, ParseStepMatcher, MethodNameStepMatcher]
        matcher = self._create_matcher(suite, matchers)
        if show_all_missing:
            step_matcher_visitor = StepMatcherVisitor(suite, matcher)
            self.steps[0].evaluate_steps(step_matcher_visitor)
        if formatter is None:
            formatter = NullFormatter()
        test_visitor = TestVisitor(suite, matcher, formatter)
        try:
            self.steps[0].evaluate_steps(test_visitor)
        except SyntaxError as exc:
            raise
        except Exception as exc:
            fix_exception_encoding(exc)
            raise

    def _create_matcher(self, suite, matcher_classes):
        root_matcher = None
        for matcher_class in matcher_classes:
            matcher = matcher_class(suite)
            if root_matcher is not None:
                root_matcher.add_matcher(matcher)
            else:
                root_matcher = matcher
        return root_matcher

    def report(self, suite, visitor_class=ReportVisitor):
        rv = visitor_class(suite)
        self.steps[0].evaluate_steps(rv)
        return rv
