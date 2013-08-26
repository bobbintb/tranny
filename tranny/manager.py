# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from threading import Thread
from time import sleep
from . import datastore
from .provider.rss import RSSFeed
from .extensions import db
from .models import DownloadEntity
from sqlalchemy.exc import DBAPIError
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
        self._client = self.init_client()
        self._watch = FileWatchService(self._client)

    def init_client(self):
        return init_client()

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
        sleep(1)

    def update_services(self):
        """ Update the provided services """
        for service in self._services:
            for torrent in service.find_matches():
                try:
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
            for torrent in feed.find_matches():
                try:
                    dl_path = config.get_download_path(torrent.section, torrent.release_name)
                    if self._client.add(torrent.torrent_data, download_dir=dl_path):
                        logger.info("Added release: {0}".format(torrent.release_name))
                        release_key = datastore.generate_release_key(torrent.release_name)
                        section = datastore.get_section(torrent.section)
                        source = datastore.get_source(feed.name)
                        download = DownloadEntity(release_key, torrent.release_name, section.section_id,
                                                  source.source_id)
                        db.session.add(download)
                        db.session.commit()
                    else:
                        logger.warn("Failed to add release: {}".format(torrent.release_name))
                except DBAPIError as err:
                    logger.exception(err)
                    db.session.rollback()
                except Exception as err:
                    logger.exception(err)

    def start(self):
        self._updater.start()
