from logging import getLogger, basicConfig
from exceptions import ConfigError
from rpc.transmission import TransmissionClient
from tranny.watch import FileWatchService
from tranny.configuration import Configuration
from tranny.rss import RSSFeed
from tranny.net import download, fetch_url
from tranny import db

# Current run state
running = False

client = None
datastore = None
config = None
watcher = None
wait_time = 1

# Running services
services = []

# Running RSS Feeds
feeds = []

log = getLogger("tranny.main")


def init_config(config_file=None):
    global config

    if not config:
        config = Configuration()
        config.initialize(config_file)
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
    enabled_client = config.get_default("general", "client", "transmission").lower()
    if enabled_client == "transmission":
        from tranny.rpc.transmission import TransmissionClient as rpc_client
    else:
        raise ConfigError("Invalid client type supplied: {0}".format(enabled_client))
    client = rpc_client(config)
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
    global datastore

    if not datastore:
        # Setup the configured datastore
        if config.get("db", "type") == "memory":
            from tranny.db.mem import MemoryStore as Datastore
        else:
            from tranny.db.gherkin import GherkinStore as Datastore
        datastore = Datastore()
        log.debug("Loaded {0} cached entries".format(datastore.size()))
    return datastore


def start():
    """ Start up all the backend services of the application """
    global config, feeds, services

    init_config()
    init_logging()
    init_watcher()
    init_client()

    feeds = [RSSFeed(config, feed_section) for feed_section in config.find_sections("rss_")]
    service_list = [section for section in config.find_sections("service_") if config.getboolean(section, "enabled")]
    for service_name in service_list:
        from tranny.service.broadcastthenet import BroadcastTheNet

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
                    _datastore.add(release_key, section=torrent.section, source=service.name)
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
                    release_key = db.generate_release_key(torrent.release_name)
                    datastore.add(release_key, section=torrent.section, source=feed.name)
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
    except:
        pass
    finally:
        log.info("Exiting")
        datastore.sync()
        watcher.stop()







