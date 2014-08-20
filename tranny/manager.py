# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import threading
from gevent import sleep, monkey
# Use gevent compatible Threads which turn into gevent coroutines
monkey.patch_all()

from sqlalchemy.exc import DBAPIError
from tranny import app, datastore, watch, models, client
from tranny.provider.rss import RSSFeed
from tranny.extensions import db
from tranny.service import tmdb


class ServiceManager(object):
    """
    Manages all the backend services enabled in the config
    """
    def __init__(self):

        self.feeds = []
        self.services = []
        self.client = None
        self._updater = threading.Thread(target=self.update)
        self._updater.daemon = False
        self.watch = None

    def reload(self):
        pass

    def init(self):
        try:
            tmdb_api_key = app.config.get("themoviedb", "api_key")
        except:
            pass
        else:
            tmdb.configure(tmdb_api_key)
        self.feeds = self.init_rss()
        self.services = self.init_services()
        self.client = client.init_client()
        #self.watch = watch.FileWatchService(self)

    @staticmethod
    def init_rss():
        """ Initialize all the RSS feeds. This will load all feed even
        if they are marked disabled in the configuration file. The enable
        check is only used later on before trying to process them.

        :return: Instantiated RSS feeds
        :rtype: []RSSFeed
        """
        return [RSSFeed(feed_section) for feed_section in app.config.find_sections("rss_")]

    @staticmethod
    def init_services():
        """ Initialize and return the API based services.

        :return: Configured services API's
        :rtype: []TorrentProvider
        """
        services = []
        service_list = [section for section in app.config.find_sections("service_") if
                        app.config.getboolean(section, "enabled")]
        for service_name in service_list:
            from tranny.provider.broadcastthenet import BroadcastTheNet

            service = BroadcastTheNet(app.config, service_name)
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
        # gevent.sleep used to yield the coroutine since the Thread is now a cooroutine
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
                dl_path = app.config.get_download_path(torrent.section, torrent.release_name)
            res = self.client.add(torrent.torrent_data, download_dir=dl_path)
            if res:
                app.logger.info("Added release: {0}".format(torrent.release_name))
                release_key = datastore.generate_release_key(torrent.release_name)
                section = datastore.get_section(torrent.section)
                source = datastore.get_source(service.name)
                download = models.DownloadEntity(release_key, torrent.release_name, section.section_id,
                                          source.source_id)
                db.session.add(download)
                db.session.commit()
        except DBAPIError as err:
            app.logger.exception(err)
            db.session.rollback()
        except Exception as err:
            app.logger.exception(err)

    def update_providers(self):
        """ Update the provided services """
        for service in self.feeds + self.services:
            for torrent in service.find_matches():
                self.add(torrent, service)

    def start(self):
        self._updater.start()
