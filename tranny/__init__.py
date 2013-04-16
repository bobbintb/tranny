from time import time, sleep
from logging import getLogger
from base64 import b64encode
from exceptions import ConfigError
from tranny.configuration import Configuration
from tranny.rss import RSSFeed
from tranny.net import download, fetch_url
from tranny import db


config = None
if not config:
    config = Configuration()
    config.initialize()

# Current run state
running = False


class Tranny:
    feeds = []
    datastore = None
    client = None

    def __init__(self, wait_time=1):
        self.wait_time = wait_time
        self.log = getLogger("tranny.main")
        self.log.info("Tranny initializing")
        self.client = self._init_client()
        self.datastore = self._init_db()

    def _init_client(self):
        enabled_client = config.get_default("general", "client", "transmission").lower()
        if enabled_client == "transmission":
            from tranny.rpc.transmission import TransmissionClient as rpc_client
        else:
            raise ConfigError("Invalid client type supplied: {0}".format(enabled_client))
        client = rpc_client(config)
        return client

    def _init_db(self):
        if config.get("db", "type") == "memory":
            from tranny.db.mem import MemoryStore as Datastore
        else:
            from tranny.db.gherkin import GherkinStore as Datastore
        return Datastore()

    def init(self):
        self.feeds = [RSSFeed(**feed) for feed in config.rss_feeds]

    def run_forever(self):
        running = True
        while running:
            for feed in self.feeds:
                try:
                    for release_name, torrent_data, section in feed.find_matches():
                        dl_path = config.get_download_path(section, release_name)
                        res = self.client.add(b64encode(torrent_data), download_dir=dl_path)
                        self.log.info("Added release: {0}".format(release_name))
                        self.datastore.add(release_name, section=section, source=feed.name)
                except Exception as err:
                    self.log.exception("Error updating feed")

