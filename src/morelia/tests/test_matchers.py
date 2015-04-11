import unittest

from mock import Mock, sentinel, patch, MagicMock

from morelia.matchers import ByNameStepMatcher, IStepMatcher


class TestStepMatcher(IStepMatcher):
    def match(self, predicate, augmented_predicate, step_methods):
        pass


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
            match.return_value = (sentinel.method, [])
            method, matches = obj.find(predicate, augmented_predicate, step_methods)
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
                match.return_value = (sentinel.method, [])
                method, matches = obj.find(predicate, augmented_predicate)
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
            match.return_value = (None, [])
            method, matches = obj.find(predicate, augmented_predicate, step_methods)
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
            match.return_value = (None, [])
            with patch.object(matcher2, 'find') as find:
                find.return_value = (sentinel.method, [])
                method, matches = matcher1.find(predicate, augmented_predicate, step_methods)
                match.assert_called_once_with(predicate, augmented_predicate, step_methods)
                # Assert
                find.assert_called_once_with(predicate, augmented_predicate, step_methods)
                self.assertEqual(method, sentinel.method)


class IStepMatcherGetAllStepMethodsTestCase(unittest.TestCase):
    """ Test :py:meth:`IStepMatcher._get_all_step_methods`. """

    def test_should_return_steps_list(self):
        """ Scenariusz: Opis scenariusza """
        # Arrange
        step_methods = ['step_method1', 'step_method2']
        suite = MagicMock()
        suite.__dir__ = Mock(return_value=step_methods)
        obj = TestStepMatcher(suite)
        # Act
        result = obj._get_all_step_methods()
        # Assert
        self.assertEqual(result, step_methods)


class ByNameStepMatcherMatchTestCase(unittest.TestCase):
    """ Test :py:meth:`ByNameStepMatcher.match`. """

    def test_should_return_name_and_method(self):
        """ Scenario: match by name """
        # Arrange
        predicate = 'my_milkshake'
        augmented_predicate = 'my_milkshake'
        method_name = 'step_%s' % predicate
        methods = {
            method_name: sentinel.method
        }
        suite = Mock(**methods)
        obj = ByNameStepMatcher(suite)
        # Act
        result_method, result_args = obj.match(predicate, augmented_predicate, methods.keys())
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
        obj = ByNameStepMatcher(suite)
        # Act
        result_method, result_args = obj.match(predicate, augmented_predicate, methods.keys())
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
        obj = ByNameStepMatcher(suite)
        # Act
        result_method, result_args = obj.match(predicate, augmented_predicate, methods.keys())
        # Assert
        self.assertEqual(result_method, None)


if __name__ == '__main__':  # pragma: nobranch
    unittest.main()
