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
import re
import textwrap


from morelia.formatters import NullFormatter
from morelia.grammar import (
    Feature,
    Background,
    Scenario,
    Given,
    When,
    Then,
    And,
    But,
    Row,
    Comment,
    Examples,
    Step,
)
from morelia.matchers import RegexpStepMatcher, ParseStepMatcher, MethodNameStepMatcher
from morelia.visitors import TestVisitor, StepMatcherVisitor
from morelia.i18n import TRANSLATIONS


class AST:
    def __init__(
        self,
        steps,
        test_visitor_class=TestVisitor,
        matcher_visitor_class=StepMatcherVisitor,
    ):
        self.steps = steps
        self._test_visitor_class = test_visitor_class
        self._matcher_visitor_class = matcher_visitor_class

    def evaluate(self, suite, formatter=None, matchers=None, show_all_missing=True):
        if matchers is None:
            matchers = [RegexpStepMatcher, ParseStepMatcher, MethodNameStepMatcher]
        matcher = self._create_matchers_chain(suite, matchers)
        feature = self.steps[0]
        if show_all_missing:
            matcher_visitor = self._matcher_visitor_class(suite, matcher)
            feature.accept(matcher_visitor)
            matcher_visitor.report_missing()
        if formatter is None:
            formatter = NullFormatter()
        test_visitor = self._test_visitor_class(suite, matcher, formatter)
        feature.accept(test_visitor)

    def _create_matchers_chain(self, suite, matcher_classes):
        root_matcher = None
        for matcher_class in matcher_classes:
            matcher = matcher_class(suite)
            try:
                root_matcher.add_matcher(matcher)
            except AttributeError:
                root_matcher = matcher
        return root_matcher


class Parser:
    def __init__(self, language=None):
        self.thangs = [
            Feature,
            Background,
            Scenario,
            Given,
            When,
            Then,
            And,
            But,
            Row,
            Comment,
            Examples,
            Step,
        ]
        self.steps = []
        if language is None:
            language = "en"
        self._language = language
        self._prepare_patterns(language)

    def _prepare_patterns(self, language):
        self._patterns = []
        for thang in self.thangs:
            pattern = thang.get_pattern(language)
            self._patterns.append((re.compile(pattern), thang))

    def parse_as_str(self, filename, prose, scenario=None):
        ast = self.parse_features(prose, scenario=scenario)
        self.steps[0].filename = filename
        return ast

    def parse_file(self, filename, scenario=r".*"):
        with open(filename, "rb") as input_file:
            return self.parse_as_str(
                filename=filename,
                prose=input_file.read().decode("utf-8"),
                scenario=scenario,
            )

    def parse_features(self, prose, scenario=r".*"):
        self.parse_feature(prose)

        # Filter steps to only include requested scenarios
        try:
            scenario_re = re.compile(scenario)
        except Exception as e:
            raise SyntaxError(
                'Invalid scenario matching regex "{}": {}'.format(scenario, e)
            )

        matched_feature_steps = []
        matched_steps = []
        matching = True
        for s in self.steps:
            if isinstance(s, Background):
                matched_feature_steps.append(s)
                matching = True
            elif isinstance(s, Scenario):
                matching = scenario_re.match(s.predicate) is not None
                if matching is True:
                    matched_feature_steps.append(s)
            if matching is True:
                matched_steps.append(s)
        self.steps = matched_steps
        self.steps[0].steps = matched_feature_steps

        ast = AST(self.steps)
        feature = self.steps[0]
        assert isinstance(feature, Feature), "Exactly one Feature per file"
        feature.enforce(
            any(isinstance(step, Scenario) for step in feature.steps),
            "Feature without Scenario(s)",
        )
        return ast

    def _parse_line(self, line):
        if self._language_parser.parse(line):
            self._prepare_patterns(self._language_parser.language)
            return

        if self._labels_parser.parse(line):
            return

        if self._docstring_parser.parse(line):
            previous = self.steps[-1]
            previous.payload = self._docstring_parser.payload
            return

        if self._anneal_last_broken_line(line):
            return

        if self._parse_thang(line):
            return

        if 0 < len(self.steps):
            self._append_to_previous_node(line)
        else:
            s = Step("???", line)
            s.line_number = self._line_producer.line_number
            feature_name = TRANSLATIONS[self._language_parser.language].get(
                "feature", "Feature"
            )
            feature_name = feature_name.replace("|", " or ")
            s.enforce(False, "feature files must start with a %s" % feature_name)

    def parse_feature(self, lines):
        self._line_producer = LineSource(lines)
        self._docstring_parser = DocStringParser(self._line_producer)
        self._language_parser = LanguageParser(default_language=self._language)
        self._labels_parser = LabelParser()
        try:
            while True:
                line = self._line_producer.get_line()
                if line:
                    self._parse_line(line)
        except StopIteration:
            pass
        return self.steps

    def _anneal_last_broken_line(self, line):
        if self.steps == []:
            return False
        last_line = self.last_node.predicate

        if re.search(r"\\\s*$", last_line):
            last = self.last_node
            last.predicate += "\n" + line
            return True

        return False

    def _parse_thang(self, line):
        line = line.rstrip()

        for regexp, klass in self._patterns:
            m = regexp.match(line)

            if m and len(m.groups()) > 0:
                node = klass(**m.groupdict())
                node.add_labels(self._labels_parser.pop_labels())
                node.connect_to_parent(self.steps, self._line_producer.line_number)
                self.last_node = node
                return node

    def _append_to_previous_node(self, line):
        previous = self.steps[-1]
        previous.predicate += "\n" + line.strip()
        previous.predicate = previous.predicate.strip()
        previous.validate_predicate()


class LabelParser:
    def __init__(self, labels_pattern=r"@\w+"):
        self._labels = []
        self._labels_re = re.compile(labels_pattern)
        self._labels_prefix_re = re.compile(r"^\s*@")

    def parse(self, line):
        """Parse labels.

        :param str line: line to parse
        :returns: True if line contains labels
        :side effects: sets self._labels to parsed labels
        """
        if self._labels_prefix_re.match(line):
            matches = self._labels_re.findall(line)
            if matches:
                self._labels.extend(matches)
                return True
        return False

    def pop_labels(self):
        """Return labels.

        :returns: labels
        :side effects: clears current labels
        """
        labels = [label.strip("@") for label in self._labels]
        self._labels = []
        return labels


class LanguageParser:
    def __init__(self, lang_pattern=r"^# language: (\w+)", default_language=None):
        if default_language is None:
            default_language = "en"
        self._language = default_language
        self._lang_re = re.compile(lang_pattern)

    def parse(self, line):
        """Parse language directive.

        :param str line: line to parse
        :returns: True if line contains language directive
        :side effects: sets self.language to parsed language
        """
        match = self._lang_re.match(line)
        if match:
            self._language = match.groups()[0]
            return True
        return False

    @property
    def language(self):
        return self._language


class DocStringParser:
    def __init__(self, source, pattern=r'\s*"""\s*'):
        self._source = source
        self._docstring_re = re.compile(pattern)
        self._payload = []

    def parse(self, line):
        """Parse docstring payload.

        :param str line: first line to parse
        :returns: True if docstring parsed
        :side effects: sets self.payload to parsed docstring
        """
        match = self._docstring_re.match(line)
        if match:
            start_line = line
            self._payload = []
            line = self._source.get_line()
            while line != start_line:
                self._payload.append(line)
                line = self._source.get_line()
            return True
        return False

    @property
    def payload(self):
        return textwrap.dedent("\n".join(self._payload))


class LineSource:
    def __init__(self, text):
        self._lines = iter([line for line in text.split("\n") if line])
        self._line_number = 0

    def get_line(self):
        """Return next line.

        :returns: next line of text
        """
        self._line_number += 1
        return next(self._lines)

    @property
    def line_number(self):
        return self._line_number
