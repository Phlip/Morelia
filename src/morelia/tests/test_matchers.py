import unittest

from mock import Mock, sentinel, patch, MagicMock

from morelia.matchers import (MethodNameStepMatcher, IStepMatcher,
                              RegexpStepMatcher, ParseStepMatcher)


class TestStepMatcher(IStepMatcher):

    def match(self, predicate, augmented_predicate, step_methods):
        pass  # pragma: nocover

    def suggest(self, predicate):
        pass  # pragma: nocover


class IStepMatcherAddMatcherTestCase(unittest.TestCase):
    """ Test :py:meth:`IStepMatcher.add_matcher`. """

    def test_should_add_matcher(self):
        """ Scenario: add matcher """
        # Arrange
        suite = Mock()
        matcher1 = TestStepMatcher(suite)
        matcher2 = TestStepMatcher(suite)
        # Act
        matcher1.add_matcher(matcher2)
        # Assert
        self.assertEqual(matcher1._next, matcher2)

    def test_should_delegate_adding_matcher(self):
        """ Scenario: delegating add """
        # Arrange
        suite = Mock()
        matcher1 = TestStepMatcher(suite)
        matcher2 = TestStepMatcher(suite)
        matcher3 = TestStepMatcher(suite)
        matcher1._next = matcher2
        # Act
        matcher1.add_matcher(matcher3)
        # Assert
        self.assertEqual(matcher1._next, matcher2)
        self.assertEqual(matcher2._next, matcher3)

    def test_should_chain_adding_matchers(self):
        """ Scenario: chaining """
        # Arrange
        suite = Mock()
        matcher1 = TestStepMatcher(suite)
        matcher2 = TestStepMatcher(suite)
        matcher3 = TestStepMatcher(suite)
        # Act
        matcher1.add_matcher(matcher2).add_matcher(matcher3)
        # Assert
        self.assertEqual(matcher1._next, matcher2)
        self.assertEqual(matcher2._next, matcher3)


class IStepMatcherFindTestCase(unittest.TestCase):
    """ Test :py:meth:`IStepMatcher.find`. """

    def test_should_find_method_when_step_methods_given(self):
        """ Scenario: find method when step methods given"""
        # Arrange
        suite = Mock()
        obj = TestStepMatcher(suite)
        # Act
        step_methods = sentinel.step_methods
        predicate = sentinel.predicate
        augmented_predicate = sentinel.augmented_predicate
        with patch.object(obj, 'match') as match:
            match.return_value = (sentinel.method, (), {})
            method, args, kwargs = obj.find(predicate, augmented_predicate, step_methods)
            match.assert_called_once_with(predicate, augmented_predicate, step_methods)
        # Assert
        self.assertEqual(method, sentinel.method)

    def test_should_find_method_when_no_step_methods_given(self):
        """ Scenario: no step methods """
        # Arrange
        suite = Mock()
        obj = TestStepMatcher(suite)
        # Act
        predicate = sentinel.predicate
        augmented_predicate = sentinel.augmented_predicate
        with patch.object(obj, 'match') as match:
            with patch.object(obj, '_get_all_step_methods') as _get_all_step_methods:
                _get_all_step_methods.return_value = sentinel.steps
                match.return_value = (sentinel.method, (), {})
                method, args, kwargs = obj.find(predicate, augmented_predicate)
                match.assert_called_once_with(predicate, augmented_predicate, sentinel.steps)
        # Assert
        self.assertEqual(method, sentinel.method)

    def test_should_not_find_method(self):
        """ Scenario: not found """
        # Arrange
        suite = Mock()
        obj = TestStepMatcher(suite)
        # Act
        step_methods = sentinel.step_methods
        predicate = sentinel.predicate
        augmented_predicate = sentinel.augmented_predicate
        with patch.object(obj, 'match') as match:
            match.return_value = (None, (), {})
            method, args, kwargs = obj.find(predicate, augmented_predicate, step_methods)
            match.assert_called_once_with(predicate, augmented_predicate, step_methods)
        # Assert
        self.assertEqual(method, None)

    def test_should_delegate_search(self):
        """ Scenario: delegate """
        # Arrange
        suite = Mock()
        matcher1 = TestStepMatcher(suite)
        matcher2 = TestStepMatcher(suite)
        matcher1.add_matcher(matcher2)
        # Act
        step_methods = sentinel.step_methods
        predicate = sentinel.predicate
        augmented_predicate = sentinel.augmented_predicate
        with patch.object(matcher1, 'match') as match:
            match.return_value = (None, (), {})
            with patch.object(matcher2, 'find') as find:
                find.return_value = (sentinel.method, (), {})
                method, args, kwargs = matcher1.find(predicate, augmented_predicate, step_methods)
                match.assert_called_once_with(predicate, augmented_predicate, step_methods)
                # Assert
                find.assert_called_once_with(predicate, augmented_predicate, step_methods)
                self.assertEqual(method, sentinel.method)


class IStepMatcherGetAllStepMethodsTestCase(unittest.TestCase):
    """ Test :py:meth:`IStepMatcher._get_all_step_methods`. """

    def test_should_return_steps_list(self):
        """ Scenario: filtered step lists """
        # Arrange
        step_methods = ['step_method1', 'step_method2']
        all_methods = step_methods + ['method3']
        suite = MagicMock()
        suite.__dir__ = Mock(return_value=all_methods)
        obj = TestStepMatcher(suite)
        # Act
        result = obj._get_all_step_methods()
        # Assert
        self.assertEqual(result, step_methods)


class MethodNameStepMatcherMatchTestCase(unittest.TestCase):
    """ Test :py:meth:`MethodNameStepMatcher.match`. """

    def test_should_return_method(self):
        """ Scenario: match by name """
        # Arrange
        predicate = 'my_milkshake'
        augmented_predicate = 'my_milkshake'
        method_name = 'step_%s' % predicate
        methods = {
            method_name: sentinel.method
        }
        suite = Mock(**methods)
        obj = MethodNameStepMatcher(suite)
        # Act
        result_method, result_args, result_kwargs = obj.match(predicate, augmented_predicate, methods.keys())
        # Assert
        self.assertEqual(result_method, sentinel.method)

    def test_should_return_none_if_method_not_found(self):
        """ Scenario: no method """
        # Arrange
        predicate = 'not there'
        augmented_predicate = 'my_milkshake'
        method_name = 'step_%s' % predicate
        methods = {
            method_name: sentinel.method
        }
        suite = Mock(**methods)
        obj = MethodNameStepMatcher(suite)
        # Act
        result_method, result_args, result_kwargs = obj.match(predicate, augmented_predicate, methods.keys())
        # Assert
        self.assertEqual(result_method, None)

    def test_should_return_none_if_method_name_too_short(self):
        """ Scenario: method too short """
        # Arrange
        predicate = 'my milk'
        augmented_predicate = 'my_milkshake'
        method_name = 'step_%s' % predicate
        methods = {
            method_name: sentinel.method
        }
        suite = Mock(**methods)
        obj = MethodNameStepMatcher(suite)
        # Act
        result_method, result_args, result_kwargs = obj.match(predicate, augmented_predicate, methods.keys())
        # Assert
        self.assertEqual(result_method, None)


class MethodNameStepMatcherSuggestTestCase(unittest.TestCase):
    """ Test :py:meth:`MethodNameStepMatcher.suggest`. """

    def test_should_return_suggested_method(self):
        """ Scenariusz: suggest """
        # Arrange
        obj = MethodNameStepMatcher(sentinel.suite)
        pattern = u'    def step_%(method_name)s(self%(args)s):\n\n        # code\n        pass\n\n'
        test_data = [
            ('tastes great', 'tastes_great', ''),
            ('less filling', 'less_filling', ''),
            ('line\nfeed', 'line_feed', ''),
            ('tick\'ed\'', 'tick_ed', ''),
            ('tastes   great', 'tastes_great', ''),
            ('argu<ment>al', 'argu_ment_al', ', ment'),
            ('arg<u>ment<al>', 'arg_u_ment_al', ', u, al'),
            ('str"ing"', 'str_ing', ', ing'),
            ('"str"i"ngs"', 'str_i_ngs', ', str, ngs'),
        ]
        for predicate, method, args in test_data:
            # Act
            result = obj.suggest(predicate)
            # Assert
            expected = pattern % {
                'method_name': method,
                'args': args,
            }
            self.assertEqual(result, expected)


class DocStringStepMatcherMatchTestCase(unittest.TestCase):
    """ Test :py:meth:`DocStringStepMatcher.match`. """

    def test_should_return_method_and_args(self):
        """ Scenario: match by docstring """
        # Arrange
        predicate = 'my milkshake brings all the boys to the yard'
        augmented_predicate = 'my milkshake brings all the boys to the yard'
        method_name = 'step_%s' % predicate
        docstring = r'my milkshake brings all the (boys|girls) to (.*) yard'
        method = Mock(__doc__=docstring)
        methods = {
            method_name: method
        }
        suite = Mock(**methods)
        obj = RegexpStepMatcher(suite)
        # Act
        result_method, result_args, result_kwargs = obj.match(predicate, augmented_predicate, methods.keys())
        # Assert
        self.assertEqual(result_method, method)
        self.assertEqual(result_args, ('boys', 'the'))

    def test_should_return_method_and_kwargs(self):
        """ Scenario: match by docstring with named groups """
        # Arrange
        predicate = 'my milkshake brings all the boys to the yard'
        augmented_predicate = 'my milkshake brings all the boys to the yard'
        method_name = 'step_%s' % predicate
        docstring = r'my milkshake brings all the (?P<who>boys|girls) to (?P<other>.*) yard'
        method = Mock(__doc__=docstring)
        methods = {
            method_name: method
        }
        suite = Mock(**methods)
        obj = RegexpStepMatcher(suite)
        # Act
        result_method, result_args, result_kwargs = obj.match(predicate, augmented_predicate, methods.keys())
        # Assert
        self.assertEqual(result_method, method)
        self.assertEqual(result_kwargs, {'who': 'boys', 'other': 'the'})

    def test_should_return_method_and_kwargs_with_mixed_groups(self):
        """ Scenario: match by docstring with named and not named groups """
        # Arrange
        predicate = 'my milkshake brings all the boys to the yard'
        augmented_predicate = 'my milkshake brings all the boys to the yard'
        method_name = 'step_%s' % predicate
        docstring = r'my milkshake brings all the (?P<who>boys|girls) to (.*) yard'
        method = Mock(__doc__=docstring)
        methods = {
            method_name: method
        }
        suite = Mock(**methods)
        obj = RegexpStepMatcher(suite)
        # Act
        result_method, result_args, result_kwargs = obj.match(predicate, augmented_predicate, methods.keys())
        # Assert
        self.assertEqual(result_method, method)
        self.assertEqual(result_args, ())
        self.assertEqual(result_kwargs, {'who': 'boys'})

    def test_should_return_none_if_docstring_not_mached(self):
        """ Scenario: no match by docstring """
        # Arrange
        predicate = 'not there'
        augmented_predicate = 'not there'
        method_name = 'step_%s' % predicate
        docstring = r'my milkshake brings all the (boys|girls) to (.*) yard'
        method = Mock(__doc__=docstring)
        methods = {
            method_name: method
        }
        suite = Mock(**methods)
        obj = RegexpStepMatcher(suite)
        # Act
        result_method, result_args, result_kwargs = obj.match(predicate, augmented_predicate, methods.keys())
        # Assert
        self.assertTrue(result_method is None)
        self.assertEqual(result_args, ())

    def test_should_return_none_if_no_docstring(self):
        """ Scenario: no match by docstring """
        # Arrange
        predicate = 'my milkshake brings all the boys to the yard'
        augmented_predicate = 'my milkshake brings all the boys to the yard'
        method_name = 'step_%s' % predicate
        method = Mock(__doc__='')
        methods = {
            method_name: method
        }
        suite = Mock(**methods)
        obj = RegexpStepMatcher(suite)
        # Act
        result_method, result_args, result_kwargs = obj.match(predicate, augmented_predicate, methods.keys())
        # Assert
        self.assertTrue(result_method is None)
        self.assertEqual(result_args, ())

    def test_should_return_second_method_and_matches(self):
        """ Scenario: many methods """
        # Arrange
        predicate = 'my milkshake brings all the boys to the yard'
        augmented_predicate = 'my milkshake brings all the boys to the yard'
        method_name = 'step_%s' % predicate
        docstring = r'my milkshake brings all the (boys|girls) to (.*) yard'
        method = Mock(__doc__=docstring)
        methods = {
            method_name: method,
            'step_other': sentinel.method,
        }
        suite = Mock(**methods)
        obj = RegexpStepMatcher(suite)
        # Act
        result_method, result_args, result_kwargs = obj.match(
            predicate, augmented_predicate, [method_name, 'step_other'])
        # Assert
        self.assertEqual(result_method, method)
        self.assertEqual(result_args, ('boys', 'the'))


class DocStringStepMatcherSuggestTestCase(unittest.TestCase):
    """ Test :py:meth:`DocStringStepMatcher.suggest`. """

    def test_should_return_suggested_method(self):
        """ Scenariusz: suggest """
        # Arrange
        obj = RegexpStepMatcher(sentinel.suite)
        # Act
        pattern = u'    def step_%(method_name)s(self%(args)s):\n        %(docstring)s\n\n        # code\n        pass\n\n'
        test_data = [
            ('tastes great', 'tastes_great', r"ur'tastes great'", ''),
            ('less filling', 'less_filling', r"ur'less filling'", ''),
            ('line\nfeed', 'line_feed', r"ur'line\nfeed'", ''),
            ('tick\'ed\'', 'tick_ed', r"ur'tick\'ed\''", ''),
            ('tastes   great', 'tastes_great', r"ur'tastes\s+great'", ''),
            ('argu<ment>al', 'argu_ment_al', r"ur'argu(.+)al'", ', ment'),
            ('arg<u>ment<al>', 'arg_u_ment_al', r"ur'arg(.+)ment(.+)'", ', u, al'),
            ('str"ing"', 'str_ing', 'ur\'str"([^"]+)"\'', ', ing'),
            ('"str"i"ngs"', 'str_i_ngs', 'ur\'"([^"]+)"i"([^"]+)"\'', ', str, ngs'),
        ]
        for predicate, method, docstring, args in test_data:
            result = obj.suggest(predicate)
            # Assert
            expected = pattern % {
                'method_name': method,
                'docstring': docstring,
                'args': args,
            }
            self.assertEqual(result, expected)


class ParseStepMatcherMatchTestCase(unittest.TestCase):
    """ Test :py:meth:`ParseStepMatcher.match`. """

    def test_should_return_method_and_args(self):
        """ Scenario: match by docstring """
        # Arrange
        predicate = 'my milkshake brings all the boys to the yard'
        augmented_predicate = 'my milkshake brings all the boys to the yard'
        method_name = 'step_%s' % predicate
        docstring = r'my milkshake brings all the {} to {} yard'
        method = Mock(__doc__=docstring)
        methods = {
            method_name: method
        }
        suite = Mock(**methods)
        obj = ParseStepMatcher(suite)
        # Act
        result_method, result_args, result_kwargs = obj.match(predicate, augmented_predicate, methods.keys())
        # Assert
        self.assertEqual(result_method, method)
        self.assertEqual(result_args, ('boys', 'the'))

    def test_should_return_method_and_kwargs(self):
        """ Scenario: match by docstring with named groups """
        # Arrange
        predicate = 'my milkshake brings all the boys to the yard'
        augmented_predicate = 'my milkshake brings all the boys to the yard'
        method_name = 'step_%s' % predicate
        docstring = r'my milkshake brings all the {who} to {other} yard'
        method = Mock(__doc__=docstring)
        methods = {
            method_name: method
        }
        suite = Mock(**methods)
        obj = ParseStepMatcher(suite)
        # Act
        result_method, result_args, result_kwargs = obj.match(predicate, augmented_predicate, methods.keys())
        # Assert
        self.assertEqual(result_method, method)
        self.assertEqual(result_kwargs, {'who': 'boys', 'other': 'the'})

    def test_should_return_method_args_and_kwargs_with_mixed_groups(self):
        """ Scenario: match by docstring with named and not named groups """
        # Arrange
        predicate = 'my milkshake brings all the boys to the yard'
        augmented_predicate = 'my milkshake brings all the boys to the yard'
        method_name = 'step_%s' % predicate
        docstring = r'my milkshake brings all the {who} to {} yard'
        method = Mock(__doc__=docstring)
        methods = {
            method_name: method
        }
        suite = Mock(**methods)
        obj = ParseStepMatcher(suite)
        # Act
        result_method, result_args, result_kwargs = obj.match(predicate, augmented_predicate, methods.keys())
        # Assert
        self.assertEqual(result_method, method)
        self.assertEqual(result_args, ('the',))
        self.assertEqual(result_kwargs, {'who': 'boys'})

    def test_should_return_none_if_docstring_not_mached(self):
        """ Scenario: no match by docstring """
        # Arrange
        predicate = 'not there'
        augmented_predicate = 'not there'
        method_name = 'step_%s' % predicate
        docstring = r'my milkshake brings all the {who} to {} yard'
        method = Mock(__doc__=docstring)
        methods = {
            method_name: method
        }
        suite = Mock(**methods)
        obj = ParseStepMatcher(suite)
        # Act
        result_method, result_args, result_kwargs = obj.match(predicate, augmented_predicate, methods.keys())
        # Assert
        self.assertTrue(result_method is None)
        self.assertEqual(result_args, ())

    def test_should_return_none_if_no_docstring(self):
        """ Scenario: no match by docstring """
        # Arrange
        predicate = 'my milkshake brings all the boys to the yard'
        augmented_predicate = 'my milkshake brings all the boys to the yard'
        method_name = 'step_%s' % predicate
        method = Mock(__doc__='')
        methods = {
            method_name: method
        }
        suite = Mock(**methods)
        obj = ParseStepMatcher(suite)
        # Act
        result_method, result_args, result_kwargs = obj.match(predicate, augmented_predicate, methods.keys())
        # Assert
        self.assertTrue(result_method is None)
        self.assertEqual(result_args, ())

    def test_should_return_second_method_and_matches(self):
        """ Scenario: many methods """
        # Arrange
        predicate = 'my milkshake brings all the boys to the yard'
        augmented_predicate = 'my milkshake brings all the boys to the yard'
        method_name = 'step_%s' % predicate
        docstring = r'my milkshake brings all the {who} to {} yard'
        method = Mock(__doc__=docstring)
        methods = {
            method_name: method,
            'step_other': sentinel.method,
        }
        suite = Mock(**methods)
        obj = ParseStepMatcher(suite)
        # Act
        result_method, result_args, result_kwargs = obj.match(
            predicate, augmented_predicate, [method_name, 'step_other'])
        # Assert
        self.assertEqual(result_method, method)
        self.assertEqual(result_args, ('the',))
        self.assertEqual(result_kwargs, {'who': 'boys'})


class ParseStepMatcherSuggestTestCase(unittest.TestCase):
    """ Test :py:meth:`ParseStepMatcher.suggest`. """

    def test_should_return_suggested_method(self):
        """ Scenario: suggest """
        # Arrange
        obj = ParseStepMatcher(sentinel.suite)
        # Act
        pattern = u'    def step_%(method_name)s(self%(args)s):\n        %(docstring)s\n\n        # code\n        pass\n\n'
        test_data = [
            ('tastes great', 'tastes_great', r"ur'tastes great'", ''),
            ('less filling', 'less_filling', r"ur'less filling'", ''),
            ('line\nfeed', 'line_feed', r"ur'line\nfeed'", ''),
            ('tick\'ed\'', 'tick_ed', r"ur'tick\'ed\''", ''),
            ('tastes   great', 'tastes_great', r"ur'tastes\s+great'", ''),
            ('argu<ment>al', 'argu_ment_al', r"ur'argu{ment}al'", ', ment'),
            ('arg<u>ment<al>', 'arg_u_ment_al', r"ur'arg{u}ment{al}'", ', u, al'),
            ('str"ing"', 'str_ing', 'ur\'str"{ing}"\'', ', ing'),
            ('"str"i"ngs"', 'str_i_ngs', 'ur\'"{str}"i"{ngs}"\'', ', str, ngs'),
        ]
        for predicate, method, docstring, args in test_data:
            result = obj.suggest(predicate)
            # Assert
            expected = pattern % {
                'method_name': method,
                'docstring': docstring,
                'args': args,
            }
            self.assertEqual(result, expected)
