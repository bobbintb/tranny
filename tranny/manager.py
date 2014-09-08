# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import platform
import gevent
from sqlalchemy.exc import DBAPIError
from tranny import app, datastore, watch, models, client,metadata
from tranny.exceptions import ClientError
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
        self._updater = gevent.Greenlet(self.update_providers)
        self._updater.start_later(1)
        self.watch = None
        self.services = self.init_services()
        #if platform.system() == 'Linux':
        #    self.watch = watch.FileWatchService(self)
        #else:
        #    app.logger.info("File watch service not supported under: {}".format(platform.system()))

    def reload(self):
        pass

    def init(self):
        try:
            tmdb_api_key = app.config.get("themoviedb", "api_key")
        except:
            pass
        else:
            tmdb.configure(tmdb_api_key)
        #self.watch = watch.FileWatchService(self)

    @staticmethod
    def init_services():
        """ Initialize and return the API based services.

        TODO Remove hard coded service names

        :return: Configured services API's
        :rtype: []TorrentProvider
        """
        services = []
        service_list = [s for s in app.config.find_sections("service_")]
        service_list += [s for s in app.config.find_sections("rss_")]
        for service_name in service_list:
            if service_name.startswith("rss_"):
                services.append(RSSFeed(service_name))
            elif service_name == "service_broadcastthenet":
                from tranny.provider.broadcastthenet import BroadcastTheNet
                services.append(BroadcastTheNet(service_name))
            elif service_name == 'service_ptp':
                from tranny.provider.ptp import PTP
                services.append(PTP(service_name))
            elif service_name == 'service_hdbits':
                from tranny.provider.hdbits import HDBits
                services.append(HDBits(service_name))
        return services

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
            res = client.get().add(torrent, download_dir=dl_path)
            if not res:
                raise ClientError
            app.logger.info("Added release: {0}".format(torrent.release_name))
            release_key = datastore.generate_release_key(torrent.release_name)
            section = datastore.get_section(torrent.section)
            source = datastore.get_source(service.name)
            download = models.Download(unicode(release_key), torrent.release_name, section.section_id,
                                       source.source_id)
            db.session.add(download)
            db.session.commit()
        except DBAPIError as err:
            app.logger.exception(err)
            db.session.rollback()
        except ClientError:
            app.logger.warning("Could not add torrent to client backend")
        except Exception as err:
            app.logger.exception(err)
        else:
            metadata.update_media_info(release_key)

    def update_providers(self):
        """ This is the primary process loop used to process TorrentProvider
        classes. It is run independently from the web service inside its own
        thread """
        while True:
            for service in self.services:
                for torrent in service.find_matches():
                    self.add(torrent, service)
            gevent.sleep(1)

    def start(self):
        self._updater.start()
