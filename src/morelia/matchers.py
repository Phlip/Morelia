from abc import ABCMeta, abstractmethod
import re
import unicodedata

import parse

from .utils import to_unicode


class IStepMatcher(object):
    """ Matches methods to steps.

    Subclasses should implement at least `match` and `suggest` methods.
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
        method, args, kwargs = self.match(predicate, augmented_predicate, step_methods)
        if method:
            return method, args, kwargs
        if self._next is not None:
            return self._next.find(predicate, augmented_predicate, step_methods)
        return None, (), {}

    @abstractmethod
    def match(self, predicate, augmented_predicate, step_methods):
        """ Match method from suite to given predicate.

        :param str predicate: step predicate
        :param str augmented_predicate: step augmented_predicate
        :param list step_methods: list of all step methods from suite
        :returns: (method object, args, kwargs)
        :rtype: (method, tuple, dict)
        """
        pass  # pragma: nocover

    @abstractmethod
    def suggest(self, predicate):
        """ Suggest method definition.

        Method is used to suggest methods that should be implemented.

        :param str predicate: step predicate
        :returns: (suggested method definition, suggested method name, suggested docstring)
        :rtype: (str, str, str)
        """
        pass  # pragma: nocover

    def _suggest_doc_string(self, predicate):
        predicate = predicate.replace("'", r"\'").replace('\n', r'\n')

        arguments = self._add_extra_args(r'["\<](.+?)["\>]', predicate)
        arguments = self._name_arguments(arguments)

        predicate = self.replace_placeholders(predicate, arguments)
        predicate = re.sub(r' \s+', r'\s+', predicate)

        arguments = self._format_arguments(arguments)
        return "r'%s'" % predicate, arguments

    def _name_arguments(self, extra_arguments):
        if not extra_arguments:
            return ''
        arguments = []
        number_arguments_count = sum(1 for arg_type, arg in extra_arguments
                                     if arg_type == 'number')
        if number_arguments_count < 2:
            num_suffixes = iter([''])
        else:
            num_suffixes = iter(range(1, number_arguments_count + 1))

        for arg_type, arg in extra_arguments:
            if arg_type == 'number':
                arguments.append('number%s' % next(num_suffixes))
            else:
                arguments.append(arg)
        return arguments

    def _format_arguments(self, arguments):
        if not arguments:
            return ''
        return ', ' + ', '.join(arguments)

    def replace_placeholders(self, predicate, arguments):
        predicate = re.sub(r'".+?"', '"([^"]+)"', predicate)
        predicate = re.sub(r'\<.+?\>', '(.+)', predicate)
        return predicate

    def _add_extra_args(self, matcher, predicate):
        args = re.findall(matcher, predicate)
        result = []
        for arg in args:
            try:
                float(arg)
            except ValueError:
                arg = ('id', self.slugify(arg))
            else:
                arg = ('number', arg)
            result.append(arg)
        return result

    def slugify(self, predicate):
        predicate = to_unicode(predicate)
        result = []
        for part in re.split('[^\w]+', predicate):
            part = unicodedata.normalize('NFD', part).encode('ascii', 'replace').decode('utf-8')
            part = part.replace(u'??', u'_').replace(u'?', u'')
            try:
                float(part)
            except ValueError:
                pass
            else:
                part = 'number'
            result.append(part)
        return '_'.join(result).strip('_')


class MethodNameStepMatcher(IStepMatcher):

    ''' Matcher that matches steps by method name. '''

    def match(self, predicate, augmented_predicate, step_methods):
        ''' See :py:meth:`IStepMatcher.match` '''

        clean = re.sub(r'[^\w]', '_?', predicate)
        pattern = '^step_' + clean + '$'
        regexp = re.compile(pattern)
        step_methods = [method for method in step_methods if regexp.match(method)]
        for method_name in step_methods:
            method = self._suite.__getattribute__(method_name)
            return method, (), {}
        return None, (), {}

    def suggest(self, predicate):
        ''' See :py:meth:`IStepMatcher.suggest` '''

        method_name = self.slugify(predicate)
        suggest = u'    def step_%(method_name)s(self):\n\n        raise NotImplementedError(\'%(predicate)s\')\n\n' % {
            'method_name': method_name,
            'predicate': predicate.replace("'", "\\'"),
        }
        return suggest, method_name, ''

    def slugify(self, predicate):
        predicate = to_unicode(predicate)
        predicate = unicodedata.normalize('NFD', predicate).encode('ascii', 'replace').decode('utf-8')
        predicate = predicate.replace(u'??', u'_').replace(u'?', u'')
        return re.sub(u'[^\w]+', u'_', predicate, re.U).strip('_')


class RegexpStepMatcher(IStepMatcher):

    ''' Matcher that matches steps by regexp in docstring. '''

    def match(self, predicate, augmented_predicate, step_methods):
        ''' See :py:meth:`IStepMatcher.match` '''

        for method_name in step_methods:
            method = self._suite.__getattribute__(method_name)
            doc = method.__doc__
            if not doc:
                continue
            doc = re.compile('^' + doc + '$')  # CONSIDER deal with users who put in the ^$
            m = doc.match(augmented_predicate)

            if m:
                kwargs = m.groupdict()
                if not kwargs:
                    args = m.groups()
                else:
                    args = ()
                return method, args, kwargs
        return None, (), {}

    def suggest(self, predicate):
        ''' See :py:meth:`IStepMatcher.suggest` '''

        docstring, extra_arguments = self._suggest_doc_string(predicate)
        method_name = self.slugify(predicate)
        suggest = u'    def step_%(method_name)s(self%(args)s):\n        %(docstring)s\n\n        raise NotImplementedError(\'%(predicate)s\')\n\n' % {
            'method_name': method_name,
            'args': extra_arguments,
            'docstring': docstring,
            'predicate': predicate.replace("'", "\\'"),
        }
        return suggest, method_name, docstring


class ParseStepMatcher(IStepMatcher):

    ''' Matcher that matches steps by format-like string in docstring. '''

    def match(self, predicate, augmented_predicate, step_methods):
        ''' See :py:meth:`IStepMatcher.match` '''

        for method_name in step_methods:
            method = self._suite.__getattribute__(method_name)
            doc = method.__doc__
            if not doc:
                continue
            match = parse.parse(doc, augmented_predicate)
            if match:
                args = match.fixed
                kwargs = match.named
                return method, tuple(args), kwargs
        return None, (), {}

    def suggest(self, predicate):
        ''' See :py:meth:`IStepMatcher.suggest` '''

        docstring, extra_arguments = self._suggest_doc_string(predicate)
        method_name = self.slugify(predicate)
        suggest = u'    def step_%(method_name)s(self%(args)s):\n        %(docstring)s\n\n        raise NotImplementedError(\'%(predicate)s\')\n\n' % {
            'method_name': method_name,
            'args': extra_arguments,
            'docstring': docstring,
            'predicate': predicate.replace("'", "\\'"),
        }
        return suggest, method_name, docstring

    def replace_placeholders(self, predicate, arguments):
        arguments = iter(arguments)

        def repl(match):
            if match.group(0).startswith('"'):
                return '"{%s}"' % next(arguments)
            return '{%s}' % next(arguments)

        predicate = re.sub(r'".+?"|\<.+?\>', repl, predicate)
        return predicate
