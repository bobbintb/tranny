# -*- coding: utf-8 -*-

import logging
import os
from os.path import exists, dirname, join, expanduser, abspath
from os import mkdir
from tranny.exceptions import ConfigError
from tranny import util

log = logging.getLogger(__name__)

from configparser import RawConfigParser as ConfigParser, NoOptionError, NoSectionError


class Configuration(ConfigParser):
    """
    Extend the built in ConfigParser module to provide some helper functions specific
    to tranny's configuration
    """
    _config_path = None
    _loaded_configs = []
'''
    def __init__(self, path="~/.config/tranny"):
        ConfigParser.__init__(self)

        self.config_file = abspath(join(dirname(dirname(__file__)), "tranny.ini"))
        try:
            loaded = self.read([self.config_file])
            if not len(loaded) == 1:
                raise ConfigError("Failed to load configuration")
        except IOError:
            raise ConfigError("No config file found: {}".format(self.config_file))
        self.config_path = expanduser(path)
        self.cache_path = join(self.config_path, 'cache_path')
        self.cache_file = join(self.cache_path, "cache.dbm")
        self.configured = False
'''
    def rules(self):
        pass

    def read(self, file_names):
        """Read and parse a filename or a list of filenames.

        This function only add debug logging output, otherwise its the same as
        ConfigParser.read.

        :return: Return list of successfully read files.
        :rtype: []unicode
        """
        if isinstance(file_names, str):
            file_names = [file_names]
        new_configs = [c for c in file_names if c not in self._loaded_configs]
        if not new_configs:
            return []
        loaded = ConfigParser.read(self, new_configs)
        self._loaded_configs.extend(loaded)
        log.debug("Read config file: {}".format(file_names))
        return loaded

    def get_default_boolean(self, section, option, default=None):
        try:
            value = self.get(section, option)
        except (NoSectionError, NoOptionError):
            return default
        else:
            if value.lower() not in self._boolean_states:
                raise ValueError('Not a boolean: {}'.format(value))
            return self._boolean_states[value.lower()]

    def get_default(self, section, option, default=False, cast=None):
        """ Fetch a config value from the database with an optional default value to use
        if the config does not exist.

        :param section:
        :type section: unicode
        :param option:
        :type option: unicode
        :param default:
        :type default: unicode, int
        :param cast:
        :type cast: callable
        :return:
        :rtype: value
        """
        try:
            value = self.get(section, option)
        except (NoSectionError, NoOptionError):
            value = default
        else:
            if value == '':
                value = default
        if cast and callable(cast):
            return cast(value)
        return value

    @staticmethod
    def find_config(config_name="tranny.ini"):
        """ Attempt to find a configuration file to load. This function first attempts
         the users home directory standard location (~/.config/tranny). If that fails it
         moves on to configuration files in the source tree root directory.

        :param config_name: Path of the config file
        :type config_name: unicode
        :return:
        :rtype:
        """
        # Try and get project source root config
        base_path = dirname(dirname(__file__))
        config_path = join(base_path, config_name)
        if exists(config_path):
            return config_path

        # Try and get home dir config
        xdg_home = os.environ.get("XDG_CONFIG_HOME")
        if not xdg_home:
            xdg_home = os.path.expanduser(os.path.join("~", ".config"))
        home_config = join(xdg_home, "/tranny/{0}".format(config_name))
        if exists(home_config):
            return home_config

        # No configs were found
        return False

    def create_dirs(self):
        """ Initialize a users config directory by creating the prerequisite directories.

        :return:
        :rtype:
        """
        if not exists(self.config_path):
            util.mkdirp(self.config_path)
        if not exists(self.cache_path):
            util.mkdirp(self.cache_path)

    def initialize(self, file_path=False):
        """ Find and load the configuration file

        .. note:: By setting the environment variable `TEST=1`, the config from the test fixture location
         will be loaded instead of the standard config locations.

        :param file_path: Optional forced file path
        :type file_path:
        :return:
        :rtype:
        """
        if os.environ.get('TEST', False):
            file_path = join(dirname(dirname(__file__)), 'tests', 'fixtures', 'test_config.ini')
            log.warning("Using TEST config file! [{}]".format(file_path))
        if not file_path:
            # Only create default locations when we are not specifying a config explicitly
            self.create_dirs()
            file_path = self.find_config()
        try:
            resp = self.read(file_path)
        except OSError:
            raise ConfigError("No suitable configuration found")
        else:
            log.info("Loaded config: {}".format(file_path))
            self.configured = True
            return resp

    def find_sections(self, prefix):
        sections = [section for section in self.sections() if section.startswith(prefix)]
        return sections

    @property
    def rss_feeds(self):
        return list(map(self.get_feed_config, self.find_sections("rss_")))

    def get_feed_config(self, section, def_interval=300):
        try:
            name = self.get(section, "name")
        except NoOptionError:
            name = section.split("_", 1)[1]
        try:
            interval = self.getint(section, "interval")
        except NoOptionError:
            interval = def_interval
        rss_conf = {
            'name': name,
            'interval': interval,
            'enabled': self.getboolean(section, "enabled"),
            'url': self.get(section, "url")
        }
        return rss_conf

    def build_regex_fetch_list(self, section=None, key_name="shows"):
        """
        unused?

        :param section:
        :type section:
        :param key_name:
        :type key_name:
        :return:
        :rtype:
        """
        from tranny.parser import normalize

        if section:
            name_list = [normalize(name) for name in self.get(section, key_name).split(",")]
        else:
            name_list = [self.build_regex_fetch_list(s, key_name) for s in self.find_sections("section_")]
        return [name for name in name_list if name]

    @staticmethod
    def get_unique_section_name(section_name, sep="_"):
        try:
            return sep.join(section_name.split(sep)[1:])
        except Exception:
            return section_name

    def get_download_path(self, section, release_info):
        """

        :param section:
        :param release_info: tranny.parser.ReleaseInfo
        :return: :rtype:
        """
        dl_path = self.get(section, "dl_path")
        #if not exists(dl_path):
        #    raise IOError("Invalid download path root: {0}".format(dl_path))
        full_dl_path = join(dl_path, ".".join(release_info['title'].split(" ")))
        if not exists(full_dl_path):
            try:
                mkdir(full_dl_path)
            except OSError:
                # Cant create presumably remote directory?
                pass
        return full_dl_path

    def get_db_uri(self, section='db', key='uri'):
        """ Get the path to the history db used by the shelve module

        :return:
        :rtype:
        """
        default_uri = "sqlite:///{}".format(expanduser("~/.config/tranny/tranny.sqlite"))
        uri = self.get_default(section, key, default_uri)
        if not uri:
            uri = default_uri
        return uri

    def get_proxies(self):
        proxies = {}
        try:
            if self.getboolean("proxy", "enabled"):
                proxy = self.get("proxy", "server")
                if proxy:
                    proxies['http'] = proxy
                    proxies['https'] = proxy
        except (NoSectionError, NoOptionError):
            pass
        finally:
            return proxies

    def get_filters(self, section, quality):
        try:
            titles = self.get(section, "quality_{}".format(quality)).split(",")
            return self._normalize_filter_names(titles)
        except (NoSectionError, NoOptionError):
            return []

    def set_filters(self, section, quality, titles):
        """ Update the config file with new filters for a section/quality filter

        :param section: Config section
        :type section: string
        :param quality: Quality keyword (sd/hd)
        :type quality: string
        :param titles: A list of titles used for the filter ['Show A', 'Show B']
        :type titles: string[]
        :return: Save status
        :rtype: bool
        """
        titles = sorted(self._normalize_filter_names(titles))
        self.set(section, "quality_{}".format(quality), ", ".join(titles))
        return self.save()

    def _normalize_filter_names(self, titles):
        return list(map(self.normalize_title, titles))

    @staticmethod
    def normalize_title(title):
        """ Normalize a title string into a format more suitable for comparisons

        :param title: Title to normalize
        :type title: string
        :return: Normalized title
        :rtype: string
        """
        return " ".join([part.capitalize() for part in title.replace(".", " ").split()])

    def save(self):
        try:
            with open(self.config_file, 'w') as config:
                self.write(config)
        except IOError:
            log.exception("Failed to write config file")
            return False
        else:
            log.info("Saved config file: {}".format(self.config_file))
            return True

    def get_section_values(self, section):
        """ Get all values stored in the config file related to a section. Hopefully
        returning correctly python typed versions of the values based on the keywords.

        :param section: Config section name
        :type section: string
        :return: dict of section key/value pairs
        :rtype: dict
        """
        values = {}
        for key in self.options(section):
            try:
                if key == "enabled":
                    values[key] = self.getboolean(section, key)
                elif self.is_int(self.get(section, key)):
                    values[key] = self.getint(section, key)
                else:
                    values[key] = self.get(section, key)
            except (NoOptionError, NoSectionError):
                pass
        return values

    def is_int(self, value):
        """ Make a guess if the config value is a integer.

        :param value: Value to check
        :type value: string
        :return: True on int value
        :rtype: bool
        """
        try:
            int(value)
        except ValueError:
            return False
        else:
            return True

    def init_app(self, app):
        """ Load the config values defined for flask into the flask application instance

        :param app: Flask application instance to initialize
        :type app: Flask
        """
        def conv_value(k, v):
            if k in ['sqlalchemy_pool_size', 'sqlalchemy_pool_timeout', 'sqlalchemy_pool_recycle']:
                return int(v)
            if k in ['sqlalchemy_echo']:
                return v.lower() != 'false'
            return v
        config_values = {k.upper(): conv_value(k, v) for k, v in list(self.get_section_values("flask").items())}
        app.config.update(config_values)
        log.info("Loaded flask config successfully")
