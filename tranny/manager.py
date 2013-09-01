# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from threading import Thread
from time import sleep
from sqlalchemy.exc import DBAPIError
from . import datastore
from .provider.rss import RSSFeed
from .extensions import db
from .models import DownloadEntity
from .watch import FileWatchService
from .app import config, logger
from .service import tmdb
from .client import init_client


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
        self._client = init_client()
        self._watch = FileWatchService(self)

    @staticmethod
    def init_rss():
        """ Initialize all the RSS feeds. This will load all feed even
        if they are marked disabled in the configuration file. The enable
        check is only used later on before trying to process them.

        :return: Instantiated RSS feeds
        :rtype: []RSSFeed
        """
        feeds = [RSSFeed(feed_section) for feed_section in config.find_sections("rss_")]
        return feeds

    @staticmethod
    def init_services():
        """ Initialize and return the API based services.

        :return: Configured services API's
        :rtype: []TorrentProvider
        """
        services = []
        service_list = [section for section in config.find_sections("service_") if
                        config.getboolean(section, "enabled")]
        for service_name in service_list:
            from tranny.provider.broadcastthenet import BroadcastTheNet

            service = BroadcastTheNet(config, service_name)
            services.append(service)
        return services

    def update(self, sleep_time=1):
        """ This is the primary process loop used to process TorrentProvider
        classes. It is run independently from the web service inside its own
        thread

        :type sleep_time: int
        :param sleep_time: Number of seconds to sleep between executing providers
        """
        self.update_providers()
        sleep(sleep_time)

    def add(self, torrent, service, dl_path=None):
        """ Handles adding a new torrent to the system. This should be considered the
        main entry point of doing this to make sure things are consistent, this cannot
        be guaranteed otherwise

        :param torrent: Torrent data named tuple containing relevant values
        :type torrent: TorrentData
        :param service: The TorrentProvider instanced used to get the torrent
        :type service: TorrentProvider
        :param dl_path: Optional download path to use for the torrent
        """
        try:
            if not dl_path:
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
        except DBAPIError as err:
            logger.exception(err)
            db.session.rollback()
        except Exception as err:
            logger.exception(err)

    def update_providers(self):
        """ Update the provided services """
        for service in self._feeds + self._services:
            for torrent in service.find_matches():
                self.add(torrent, service)

    def start(self):
        self._updater.start()
