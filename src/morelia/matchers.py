from abc import ABCMeta, abstractmethod
import re
import unicodedata

from .utils import to_unicode


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

    @abstractmethod
    def suggest(self, predicate):
        pass  # pragma: nocover

    def _suggest_doc_string(self, predicate):
        extra_arguments = ''
        predicate = predicate.replace("'", r"\'").replace('\n', r'\n')

        # support for tables
        extra_arguments += self._add_extra_args(r'\<(.+?)\>', predicate)
        predicate = re.sub(r'\<.+?\>', '(.+)', predicate)

        # support for variables
        extra_arguments += self._add_extra_args(r'"(.+?)"', predicate)
        predicate = re.sub(r'".+?"', '"([^"]+)"', predicate)

        predicate = re.sub(r' \s+', r'\s+', predicate)
        return "ur'%s'" % predicate, extra_arguments

    def _add_extra_args(self, matcher, predicate):
        args = re.findall(matcher, predicate)
        return ''.join(', ' + self.slugify(arg) for arg in args)

    def slugify(self, predicate):
        predicate = to_unicode(predicate)
        predicate = unicodedata.normalize('NFD', predicate).encode('ascii', 'replace').decode('utf-8')
        predicate = predicate.replace(u'??', u'_').replace(u'?', u'')
        return re.sub(u'[^\w]+', u'_', predicate, re.U).strip('_')


class MethodNameStepMatcher(IStepMatcher):

    def match(self, predicate, augmented_predicate, step_methods):
        clean = re.sub(r'[^\w]', '_?', predicate)
        pattern = '^step_' + clean + '$'
        regexp = re.compile(pattern)
        step_methods = [method for method in step_methods if regexp.match(method)]
        for method_name in step_methods:
            method = self._suite.__getattribute__(method_name)
            return method, []
        return None, []

    def suggest(self, predicate):
        """ Suggest method definition.

        :param str predicate: step predicate
        :returns: suggested method definition
        """
        doc_string, extra_arguments = self._suggest_doc_string(predicate)
        method_name = self.slugify(predicate)
        indent = ' ' * 4
        suggest = u'%(indent)sdef step_%(method_name)s(self%(args)s):\n\n%(double_indent)s# code\n\n' % {
            'indent': indent,
            'method_name': method_name,
            'args': extra_arguments,
            'double_indent': indent * 2,
        }
        return suggest


class DocStringStepMatcher(IStepMatcher):

    def match(self, predicate, augmented_predicate, step_methods):
        for method_name in step_methods:
            method = self._suite.__getattribute__(method_name)
            doc = method.__doc__
            if not doc:
                continue
            doc = re.compile('^' + doc + '$')  # CONSIDER deal with users who put in the ^$
            m = doc.match(augmented_predicate)

            if m:
                return method, m.groups()
        return None, []

    def suggest(self, predicate):
        """ Suggest method definition.

        :param str predicate: step predicate
        :returns: suggested method definition
        """
        doc_string, extra_arguments = self._suggest_doc_string(predicate)
        method_name = self.slugify(predicate)
        indent = ' ' * 4
        suggest = u'%(indent)sdef step_%(method_name)s(self%(args)s):\n%(double_indent)s%(doc_string)s\n\n%(double_indent)s# code\n\n' % {
            'indent': indent,
            'method_name': method_name,
            'args': extra_arguments,
            'double_indent': indent * 2,
            'doc_string': doc_string
        }
        return suggest
