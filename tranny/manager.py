# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import logging
import gevent
from socketio.server import SocketIOServer
from sqlalchemy.exc import DBAPIError
from tranny import app
from tranny import datastore
from tranny import watch
from tranny import client
from tranny import metadata
from tranny.app import config, Session, engine, Base
from tranny.exceptions import ClientError
from tranny.models import Download
from tranny.provider.rss import RSSFeed

log = logging.getLogger(__name__)


class ServiceManager(object):
    """
    Manages all the backend services enabled in the config. This would be considered
    the core off the application containing its main event loop process
    """

    def __init__(self):

        self.feeds = []
        self.services = []
        self.webui = None
        self.client = None
        self.init_db()
        self._updater = gevent.Greenlet(self.update_providers)
        self._updater.start_later(1)
        self.watch = None
        self.init_providers()
        app.torrent_client = client.init_client()
        if config.getboolean("webui", "enabled"):
            self.init_webui()

        # TODO Watch service is hanging at the moment, needs to be looked into
        # if platform.system() == 'Linux':
        #    self.watch = watch.FileWatchService(self)
        #else:
        #    log.info("File watch service not supported under: {}".format(platform.system()))

    def reload(self):
        self._updater.kill()
        config.initialize()

    def init_db(self):
        """ Bind our sqlalchemy engine and create any missing tables """
        Session.configure(bind=engine)
        Base.metadata.create_all(bind=engine)

    def init_webui(self):
        """ Initialize and start the flask based webui. This does not check if it is
        enabled, so that must happen prior to calling this

        :return:
        :rtype:
        """
        host = config.get_default('flask', 'listen_host', 'localhost')
        port = config.get_default('flask', 'listen_port', 5000, int)
        from tranny.app import create_app

        wsgi_app = create_app()
        socketio_app = SocketIOServer((host, port), wsgi_app, resource='socket.io')
        socketio_app.serve_forever()

    def init_providers(self):
        """ Initialize and return the API based services.

        TODO Remove hard coded service names

        :return: Configured services API's
        :rtype: []TorrentProvider
        """
        self.services = []
        service_list = [s for s in app.config.find_sections("provider_")]
        service_list += [s for s in app.config.find_sections("rss_")]
        for service_name in service_list:
            if service_name.startswith("rss_"):
                self.services.append(RSSFeed(service_name))
            elif service_name == "provider_broadcastthenet":
                from tranny.provider.broadcastthenet import BroadcastTheNet

                self.services.append(BroadcastTheNet(service_name))
            elif service_name == 'provider_ptp':
                from tranny.provider.ptp import PTP

                self.services.append(PTP(service_name))
            elif service_name == 'provider_hdbits':
                from tranny.provider.hdbits import HDBits

                self.services.append(HDBits(service_name))
        return self.services

    def add(self, session, torrent, service, dl_path=None):
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
            log.info("Added release: {0}".format(torrent.release_name))
            release_key = datastore.generate_release_key(torrent.release_name)
            section = datastore.get_section(session, torrent.section)
            source = datastore.get_source(session, service.name)
            download = Download(release_key.as_unicode(), torrent.release_name, section.section_id,
                                source.source_id)
            session.add(download)
            session.commit()
        except DBAPIError as err:
            log.exception(err)
            session.rollback()
        except ClientError:
            log.warning("Could not add torrent to client backend")
        except Exception as err:
            log.exception(err)
        else:
            metadata.update_media_info(release_key)

    def update_providers(self):
        """ This is the primary process loop used to process TorrentProvider
        classes. It is run independently from the web service inside its own
        thread """
        while True:
            for service in self.services:
                for torrent, session in service.find_matches():
                    self.add(session, torrent, service)
            gevent.sleep(1)

    def start(self):
        self._updater.start()
        while True:
            gevent.sleep(0.1)
