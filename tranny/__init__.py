from logging import getLogger, basicConfig
from time import sleep
from tranny.exceptions import ConfigError
from tranny.client.transmission import TransmissionClient
from tranny.configuration import Configuration
from tranny import datastore
from tranny.provider.rss import RSSFeed
from tranny.net import download, fetch_url
from tranny.watch import FileWatchService
from tranny import web

# Current run state
running = False

client = None
db = None
config = None
watcher = None
wait_time = 1

# Running services
services = []

# Running RSS Feeds
feeds = []

log = getLogger("tranny.main")


class TrannyException(Exception):
    pass


def get_config():
    global config
    if not config:
        return init_config()
    return config


def init_config(config_file=None, reload_config=False):
    global config

    if not config or reload_config:
        config = Configuration()
        config.initialize(config_file)
        log.info("Initialized configuration")
    return config


def init_logging():
    """ Setup the logger service """
    if config.getboolean("log", "enable"):
        basicConfig(
            level=config.get_default('log', 'level', 10, int),
            format=config.get_default('log', 'format', "%(asctime)s - %(message)s", str),
            datefmt=config.get_default('log', 'datefmt', "%Y-%m-%d %H:%M:%S", str)
        )


def init_client():
    """ Initialize the torrent client being used to handle the torrent data retreived.

    :return:
    :rtype: TransmissionClient
    """
    global client
    if not client:
        enabled_client = config.get_default("general", "client", "transmission").lower()
        if enabled_client == "transmission":
            from tranny.client.transmission import TransmissionClient as TorrentClient
        elif enabled_client == "utorrent":
            from tranny.client.utorrent import UTorrentClient as TorrentClient
        else:
            raise ConfigError("Invalid client type supplied: {0}".format(enabled_client))
        client = TorrentClient(config)
    return client


def init_watcher():
    """ Start configured services

    :return:
    :rtype: FileWatchService
    """
    global watcher

    if not watcher:
        watcher = FileWatchService(config)
    return watcher


def init_datastore():
    global db

    if not db:
        # Setup the configured datastore
        if config.get("db", "type") == "memory":
            from tranny.datastore.adapters.mem import MemoryStore as Datastore
        elif config.get("db", "type") == "sqlite":
            from tranny.datastore.adapters.sqlite import SQLiteStore as Datastore
        elif config.get("db", "type") == "mysql":
            from tranny.datastore.adapters.mysql import MySQLStore as Datastore
        else:
            raise ConfigError("Invalid datastore type: {0}".format(config.get("db", "type")))
        db = Datastore(config)
        log.info("Loaded {0} cached entries".format(db.size()))
    return db


def init_webui(section_name="webui"):
    global config
    if config.getboolean(section_name, "enabled"):
        log.debug("WebUI enabled, starting.")
        hostname = config.get(section_name, "listen_host")
        port = config.getint(section_name, "listen_port")
        debug = config.getboolean(section_name, "enabled")
        web.start(listen_host=hostname, listen_port=port, debug=debug)
    else:
        log.debug("WebUI disabled, not starting.")


def start():
    """ Start up all the backend services of the application """
    init_config()
    init_logging()
    init_datastore()
    init_watcher()
    init_client()
    init_webui()
    reload_conf()


def reload_conf():
    """ Reload all services with new configuration settings

    :return:
    :rtype:
    """
    global config, feeds, services
    init_config()
    try:
        tmdb_api_key = config.get("themoviedb", "api_key")
        from tranny import tmdb

        tmdb.configure(tmdb_api_key)
    except:
        pass
    feeds = [RSSFeed(config, feed_section) for feed_section in config.find_sections("rss_")]
    service_list = [section for section in config.find_sections("service_") if config.getboolean(section, "enabled")]
    for service_name in service_list:
        from tranny.provider.broadcastthenet import BroadcastTheNet

        service = BroadcastTheNet(config, service_name)
        services.append(service)


def update_services(services):
    """ Update the provided services

    :param services: List of services
    :type services: TorrentProvider[]
    :return:
    :rtype:
    """
    for service in services:
        try:
            for torrent in service.find_matches():
                dl_path = config.get_download_path(torrent.section, torrent.release_name)
                res = client.add(torrent.torrent_data, download_dir=dl_path)
                if res:
                    log.info("Added release: {0}".format(torrent.release_name))
                    release_key = db.generate_release_key(torrent.release_name)
                    db.add(release_key, torrent.release_name, section=torrent.section, source=service.name)
        except Exception as err:
            log.exception("Error updating service")


def update_rss(feeds):
    """ Update the provided RSS feeds

    :param feeds: Feeds to update
    :type feeds: TorrentProvider[]
    """
    for feed in feeds:
        try:
            for torrent in feed.find_matches():
                dl_path = config.get_download_path(torrent.section, torrent.release_name)
                res = client.add(torrent.torrent_data, download_dir=dl_path)
                if res:
                    log.info("Added release: {0}".format(torrent.release_name))
                    release_key = datastore.generate_release_key(torrent.release_name)
                    db.add(release_key, torrent.release_name, section=torrent.section, source=feed.name)
        except Exception as err:
            log.exception("Error updating feed")


def run_forever():
    """ Run the server under a basic event loop """
    global feeds, config, watcher

    running = True
    try:
        while running:
            update_services(services)
            update_rss(feeds)
            sleep(1)
    except:
        pass
    finally:
        log.info("Exiting")
        web.stop()
        db.sync()
        watcher.stop()







