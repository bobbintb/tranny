from threading import Thread
from . import datastore
from .exceptions import ConfigError
from .provider.rss import RSSFeed
from .extensions import db
from .models import DownloadEntity
from .watch import FileWatchService
from .app import config, logger
from .service import tmdb


class ServiceManager(object):

    def __init__(self):

        self._feeds = []
        self._services = []
        self._client = None
        self._updater = Thread(target=self.update)
        self._updater.daemon = True
        self._watch = None

    def reload(self):
        pass

    def init(self):
        try:
            tmdb_api_key = config.get("themoviedb", "api_key")
        except:
            pass
        else:
            tmdb.configure(tmdb_api_key)
        self._feeds = self.init_rss()
        self._services = self.init_services()
        self._client = self.init_client()
        self._watch = FileWatchService(self._client)

    def init_client(self):
        enabled_client = config.get_default("general", "client", "transmission").lower()
        if enabled_client == "transmission":
            from tranny.client.transmission import TransmissionClient as TorrentClient
        elif enabled_client == "utorrent":
            from tranny.client.utorrent import UTorrentClient as TorrentClient
        else:
            raise ConfigError("Invalid client type supplied: {0}".format(enabled_client))
        return TorrentClient()

    def init_rss(self):
        feeds = [RSSFeed(feed_section) for feed_section in config.find_sections("rss_")]
        return feeds

    def init_services(self):
        services = []
        service_list = [section for section in config.find_sections("service_") if
                        config.getboolean(section, "enabled")]
        for service_name in service_list:
            from tranny.provider.broadcastthenet import BroadcastTheNet

            service = BroadcastTheNet(config, service_name)
            services.append(service)
        return services

    def update(self):
        self.update_rss()
        self.update_services()

    def update_services(self):
        """ Update the provided services """
        for service in self._services:
            try:
                for torrent in service.find_matches():
                    dl_path = config.get_download_path(torrent.section, torrent.release_name)
                    res = self._client.add(torrent.torrent_data, download_dir=dl_path)
                    if res:
                        logger.info("Added release: {0}".format(torrent.release_name))
                        release_key = datastore.generate_release_key(torrent.release_name)
                        section = datastore.get_section(torrent.section)
                        source = datastore.get_source(service.name)
                        download = DownloadEntity(release_key, torrent.release_name, section.section_id,
                                                  source.source_id)
                        db.session.add(download)
                        db.commit()
            except Exception as err:
                logger.exception(err)

    def update_rss(self):
        """ Update the provided RSS feeds """
        for feed in self._feeds:
            try:
                for torrent in feed.find_matches():
                    dl_path = config.get_download_path(torrent.section, torrent.release_name)
                    res = self._client.add(torrent.torrent_data, download_dir=dl_path)
                    if res:
                        logger.info("Added release: {0}".format(torrent.release_name))
                        release_key = datastore.generate_release_key(torrent.release_name)
                        section = datastore.get_section(torrent.section)
                        source = datastore.get_source(feed.name)
                        download = DownloadEntity(release_key, torrent.release_name, section.section_id,
                                                  source.source_id)
                        db.session.add(download)
                        db.session.commit()
            except Exception as err:
                logger.exception(err)

    def start(self):
        self._updater.start()
