from time import time, sleep
from logging import getLogger, basicConfig
from base64 import b64encode
from exceptions import ConfigError
from rpc.transmission import TransmissionClient
from transmissionrpc import TransmissionError
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
feeds = []

log = getLogger("tranny.main")


def _init_logging():
    if config.getboolean("log", "enable"):
        basicConfig(
            level=config.get_default('log', 'level', 10, int),
            format=config.get_default('log', 'format', "%(asctime)s - %(message)s", str),
            datefmt=config.get_default('log', 'datefmt', "%Y-%m-%d %H:%M:%S", str)
        )


def _init_client():
    enabled_client = config.get_default("general", "client", "transmission").lower()
    if enabled_client == "transmission":
        from tranny.rpc.transmission import TransmissionClient as rpc_client
    else:
        raise ConfigError("Invalid client type supplied: {0}".format(enabled_client))
    client = rpc_client(config)
    return client


def _init_watcher():
    """ Start configured services

    :return:
    :rtype: FileWatchService
    """
    watcher = FileWatchService(config)
    return watcher


def start():
    global config, feeds, watcher

    if not watcher:
        # Setup watch dirs to start monitoring
        watcher = _init_watcher()
    feeds = [RSSFeed(**feed) for feed in config.rss_feeds]


def run_forever():
    global feeds, config, watcher
    running = True
    try:
        while running:
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
    except:
        log.info("Exiting")
        datastore.sync()
        watcher.stop()


if not config:
    # Load the config from disk
    config = Configuration()
    config.initialize()

_init_logging()

if not datastore:
    # Setup the configured datastore
    if config.get("db", "type") == "memory":
        from tranny.db.mem import MemoryStore as Datastore
    else:
        from tranny.db.gherkin import GherkinStore as Datastore
    datastore = Datastore()
    log.debug("Loaded {0} cached entries".format(datastore.size()))

if not client:
    # Setup backend client connection
    client = _init_client()
