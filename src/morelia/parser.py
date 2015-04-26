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


from .grammar import (AST, Feature, Background, Scenario, Given, When, Then,
                      And, But, Row, Comment, Examples, Step)
from .i18n import TRANSLATIONS
from .utils import to_unicode


#  TODO  what happens with blank table items?
#  ERGO  river is to riparian as pond is to ___?

LANGUAGE_RE = re.compile(r'^# language: (\w+)')
DEFAULT_LANGUAGE = 'en'


class Parser:

    def __init__(self, language=None):
        self.thangs = [
            Feature, Background, Scenario,
            Given, When, Then, And, But,
            Row, Comment, Examples, Step
        ]
        self.steps = []
        self.language = DEFAULT_LANGUAGE if language is None else language
        self._prepare_patterns(self.language)

    def _prepare_patterns(self, language):
        self._patterns = []
        for thang in self.thangs:
            pattern = thang.get_pattern(language)
            self._patterns.append((re.compile(pattern), thang))

    def parse_file(self, filename):
        prose = open(filename, 'rb').read().decode('utf-8')
        ast = self.parse_features(prose)
        self.steps[0].filename = filename
        return ast

    def parse_features(self, prose):
        self.parse_feature(prose)
        return AST(self.steps)

    def _parse_language_directive(self, line):
        """ Parse language directive.

        :param str line: line to parse
        :returns: True if line contains correct language directive
        :side effects: sets self.language to parsed language
        """
        match = LANGUAGE_RE.match(line)
        if match:
            self.language = match.groups()[0]
            self._prepare_patterns(self.language)
            return True
        return False

    def parse_feature(self, lines):
        lines = to_unicode(lines)
        self.line_number = 0

        for self.line in lines.split(u'\n'):
            self.line_number += 1

            if not self.line:
                continue

            if self._parse_language_directive(self.line):
                continue

            if self._anneal_last_broken_line():
                continue

            if self._parse_line():
                continue

            if 0 < len(self.steps):
                self._append_to_previous_node()
            else:
                s = Step('???', self.line)
                s.line_number = self.line_number
                feature_name = TRANSLATIONS[self.language].get('feature', u'Feature')
                feature_name = feature_name.replace('|', ' or ')
                s.enforce(False, u'feature files must start with a %s' % feature_name)

        return self.steps

    def _anneal_last_broken_line(self):
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

        for regexp, klass in self._patterns:
            m = regexp.match(self.line)

            if m and len(m.groups()) > 0:
                node = klass(**m.groupdict())
                node.connect_to_parent(self.steps, self.line_number)
                self.last_node = node
                return node

    def _append_to_previous_node(self):
        previous = self.steps[-1]
        previous.predicate += '\n' + self.line.strip()
        previous.predicate = previous.predicate.strip()
        previous.validate_predicate()
