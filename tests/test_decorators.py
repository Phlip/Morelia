import unittest

from mock import patch, Mock
from morelia.decorators import should_skip, tags


@tags(['unit'])
class ShouldSkipTestCase(unittest.TestCase):

    def test_should_skip(self):
        tags_list = ['tag1', 'tag2']
        test_data = [
            ('', False),
            ('-tag1', True),
            ('tag1', False),
            ('tag1 tag2', False),
            ('tag1 -tag2', True),
            ('-tag1 -tag2', True),
            ('tag3', True),
            ('-tag3', False),
            ('tag1 -tag3', False),
            ('tag1 tag2 -tag3', False),
            ('-tag1 -tag2 -tag3', True),
        ]
        for pattern, expected in test_data:
            result = should_skip(tags_list, pattern)
            self.assertEqual(result, expected)


@tags(['unit'])
class TagsTestCase(unittest.TestCase):

    def setUp(self):
        self._skip_data = [
            ([], 'tag1'),
            (['tag1'], '-tag1'),
        ]
        self._pass_data = [
            (['tag1'], 'tag1'),
            (['tag1'], ''),
            ([], '-tag1'),
        ]

    def dummy(self):
        pass

    def test_should_skip(self):
        for tags_list, pattern in self._skip_data:
            with patch('morelia.decorators.get_config') as get_config:
                get_config.return_value.get_tags_pattern.return_value = pattern
                decorated = tags(tags_list)(self.dummy)
                self.assertRaises(unittest.SkipTest, decorated)

    def test_should_not_skip(self):
        for tags_list, pattern in self._pass_data:
            with patch('morelia.decorators.get_config') as get_config:
                get_config.return_value.get_tags_pattern.return_value = pattern
                decorated = tags(tags_list)(self.dummy)
                try:
                    decorated()
                except unittest.SkipTest:  # pragma: nocover
                    self.fail('Should not raise SkipTest')  # pragma: nocover

    def test_should_skip_with_given_config(self):
        for tags_list, pattern in self._skip_data:
            config = Mock()
            config.get_tags_pattern.return_value = pattern
            decorated = tags(tags_list, config=config)(self.dummy)
            self.assertRaises(unittest.SkipTest, decorated)

    def test_should_not_skip_with_no_pattern_func(self):
        for tags_list, pattern in self._pass_data:
            config = Mock()
            config.get_tags_pattern.return_value = pattern
            decorated = tags(tags_list, config=config)(self.dummy)
            try:
                decorated()
            except unittest.SkipTest:  # pragma: nocover
                self.fail('Should not raise SkipTest')  # pragma: nocover
