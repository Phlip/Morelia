import os

from six.moves.configparser import SafeConfigParser, NoSectionError, NoOptionError


DEFAULT_CONFIG_FILES = ['.moreliarc', '~/.moreliarc', '/etc/morelia.rc']


class Config(object):
    """ Configuration object.

    Configuration is read from ini-style files and environment variables
    prefixed with `MORELIA_`.
    By default Morelia search for files:

        * .moreliarc
        * ~/.moreliarc
        * /etc/morelia.rc
    """

    def __init__(self, config_files=None, config_parser_class=None):
        self._env_prefix = 'MORELIA_'
        self._items = {
            'tags': None,
            'formatter': None,
            'matchers': None,
            'show_all_missing': False,
        }
        if config_files is None:
            config_files = DEFAULT_CONFIG_FILES
        self._default_section = 'morelia'
        self._config_files = [os.path.abspath(os.path.expandvars(os.path.expanduser(config_file)))
                              for config_file in config_files]
        if config_parser_class is None:
            config_parser_class = SafeConfigParser
        self._config_parser_class = config_parser_class

    def load(self):
        self._update_from_file()
        self._update_from_environ()

    def _update_from_file(self):
        config_parser = self._config_parser_class()
        config_parser.read(self._config_files)
        for key in self._items.keys():
            try:
                value = config_parser.get('morelia', key)
            except (NoOptionError, NoSectionError):
                pass
            else:
                self._items[key] = value

    def _update_from_environ(self):
        for key in self._items.keys():
            try:
                value = os.environ[self._env_prefix + key.upper()]
            except KeyError:
                pass
            else:
                self._items[key] = value

    def get_tags_pattern(self):
        tags = self._items.get('tags', '')
        return tags if tags is not None else ''


def get_config(_memo={}):
    try:
        return _memo['config']
    except KeyError:
        config = Config()
        config.load()
        _memo['config'] = config
    return _memo['config']
