import unittest

from mock import Mock, patch
from morelia.config import Config, get_config
from morelia.decorators import tags
from six.moves.configparser import NoSectionError, NoOptionError, SafeConfigParser


@tags(['unit'])
class ConfigGetTagsPatternTestCase(unittest.TestCase):
    """ Test :py:meth:`Config.get_tags_pattern`. """

    @patch('morelia.config.os')
    def test_should_return_tags_pattern_from_file(self, os):
        """ Scenario: tags pattern from file """
        # Arrange
        os.environ.__getitem__.side_effect = KeyError

        def config_read(section, key):
            assert section == 'morelia'
            if key == 'tags':
                return 'tag1,tag2'
            return ''
        config_parser_class = Mock()
        config_parser_class.return_value.get.side_effect = config_read
        obj = Config(config_parser_class=config_parser_class)
        obj.load()
        # Act
        pattern = obj.get_tags_pattern()
        # Assert
        self.assertEqual(pattern, 'tag1,tag2')

    @patch('morelia.config.os')
    def test_should_not_tags_pattern_from_file_if_no_option(self, os):
        """ Scenario: tags pattern from file """
        # Arrange
        os.environ.__getitem__.side_effect = KeyError

        def config_read(section, key):
            assert section == 'morelia'
            if key == 'tags':
                raise NoOptionError(None, None)
            return ''
        config_parser_class = Mock()
        config_parser_class.return_value.get.side_effect = config_read
        obj = Config(config_parser_class=config_parser_class)
        obj.load()
        # Act
        pattern = obj.get_tags_pattern()
        # Assert
        self.assertEqual(pattern, '')

    @patch('morelia.config.os')
    def test_should_not_tags_pattern_from_file_if_no_section(self, os):
        """ Scenario: tags pattern from file """
        # Arrange
        os.environ.__getitem__.side_effect = KeyError

        def config_read(section, key):
            assert section == 'morelia'
            if key == 'tags':
                raise NoSectionError(None)
            return ''
        config_parser_class = Mock()
        config_parser_class.return_value.get.side_effect = config_read
        obj = Config(config_parser_class=config_parser_class)
        obj.load()
        # Act
        pattern = obj.get_tags_pattern()
        # Assert
        self.assertEqual(pattern, '')

    @patch('morelia.config.os')
    def test_should_return_tags_pattern_from_environment(self, os):
        """ Scenario: tags pattern from environment """
        # Arrange

        def environ_get(key):
            if key == 'MORELIA_TAGS':
                return 'tag1,tag2'
            return ''
        os.environ.__getitem__.side_effect = environ_get
        config_parser_class = Mock()
        config_parser_class.return_value.get.return_value = ''
        obj = Config(config_parser_class=config_parser_class)
        obj.load()
        # Act
        pattern = obj.get_tags_pattern()
        # Assert
        self.assertEqual(pattern, 'tag1,tag2')


@tags(['unit'])
class ConfigInitTestCase(unittest.TestCase):
    """ Test :py:meth:`Config.__init__`. """

    def test_should_create_with_config_files(self):
        """ Scenario: create with config files"""
        # Arrange
        # Act
        obj = Config(config_files=['sample.cfg'])
        # Assert
        self.assertEqual(len(obj._config_files), 1)

    def test_should_create_with_default_parser(self):
        """ Scenario: create with default parser """
        # Arrange
        # Act
        obj = Config()
        # Assert
        self.assertTrue(issubclass(SafeConfigParser, obj._config_parser_class))


@tags(['unit'])
class GetConfigTestCase(unittest.TestCase):
    """ Test :py:meth:`get_config`. """

    @patch('morelia.config.Config')
    def test_should_return_config_object(self, Config):
        """ Scenario: return config object """
        # Arrange
        # Act
        config = get_config()
        # Assert
        self.assertIsNotNone(config)

    @patch('morelia.config.Config')
    def test_should_return_memoized_config_object(self, Config):
        """ Scenario: return memoized config object """
        # Arrange
        # Act
        config1 = get_config()
        config2 = get_config()
        # Assert
        self.assertIsNotNone(config1)
        self.assertEqual(config1, config2)
