# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from ConfigParser import NoOptionError, NoSectionError
from os.path import exists, isdir, dirname, basename, splitext, expanduser
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .app import config, logger
from .datastore import generate_release_key


class FileWatchService(FileSystemEventHandler):
    _path_sections = dict()

    name = "dir_watch"

    def __init__(self, service_manager):
        """

        :param service_manager:
        :type service_manager: tranny.manager.ServiceManager
        :return:
        :rtype:
        """
        self._service_manager = service_manager
        self._observer = Observer()
        for section in config.find_sections("watch"):
            try:
                section_name = config.get_default(section, "section", False)
                watch_path = config.get(section, "path")
                if not exists(watch_path):
                    logger.warn("Watch path does not exist {0}".format(watch_path))
            except (NoOptionError, NoSectionError):
                logger.warn("Failed to get dl_path key for watch section {0}. Does not exist".format(
                    section
                ))
                continue

            dl_path = expanduser(config.get("section_{0}".format(section_name), "dl_path"))
            if not dl_path or not exists(dl_path) or not isdir(dl_path):
                logger.warning("Invalid watch directory {0}".format(dl_path))
                continue
            if not config.has_section("section_{0}".format(section_name)):
                logger.warning("Invalid section name specified for watch dir: {0}".format(section_name))

            self._observer.schedule(self, watch_path, recursive=True)
            self._path_sections[watch_path] = section_name
        self._observer.start()

    def on_created(self, event):
        """ Handle a new torrent file being saved to the watch directory

        :param event: File creation event
        :type event: FileCreatedEvent
        """
        if event.src_path.lower().endswith(".torrent"):
            logger.info("Got new torrent file save event")
            torrent_name = splitext(basename(event.src_path))[0]
            dir_path = dirname(event.src_path)
            try:
                section = self._path_sections[dir_path]
            except KeyError:
                logger.error("Unknown watch path detected: {0}".format(dir_path))
                return False
            else:
                release_key = generate_release_key(torrent_name)
                dl_path = config.get_download_path("section_{}".format(section), torrent_name)
                self._service_manager.add(open(event.src_path).read(), self, dl_path=dl_path)
                #de = DownloadEntity(release_key=release_key, release_name=)
                #db.session.add(release_key, section=section, source="watch_{0}".format(section))

    def stop(self):
        self._observer.stop()
        self._observer.join()
