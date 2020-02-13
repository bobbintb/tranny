# -*- coding: utf-8 -*-

import logging
from configparser import NoOptionError, NoSectionError
from os.path import exists, isdir, dirname, basename, splitext, expanduser
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from tranny.app import config
from tranny import release

log = logging.getLogger(__name__)


class FileWatchService(FileSystemEventHandler):
    """
    Provides a TorrentProvider service for handling any number of watch folders.
    This is run independently of the service manager event loop as it uses
    watchdog's thread to watch for events. When valid events are found they are
    routed back through the same ServiceManager.add method however.
    """
    _path_sections = dict()

    name = "dir_watch"

    def __init__(self, service_manager):
        """

        :param service_manager:
        :type service_manager: tranny.manager.ServiceManager                continue
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
                    log.warn("Watch path does not exist {0}".format(watch_path))
            except (NoOptionError, NoSectionError):
                log.warn("Failed to get dl_path key for watch section {0}. Does not exist".format(
                    section
                ))
                continue

            dl_path = expanduser(config.get("section_{0}".format(section_name), "dl_path"))
            if not dl_path or not exists(dl_path) or not isdir(dl_path):
                log.warning(
                    "Invalid download directory {0}. Disabling watch service for this directory".format(dl_path)
                )
                watch_path = None
            if not config.has_section("section_{0}".format(section_name)):
                log.warning("Invalid section name specified for watch dir: {0}".format(section_name))
            if watch_path:
                self._observer.schedule(self, watch_path, recursive=True)
                self._path_sections[watch_path] = section_name
        if not self._path_sections:
            log.warning("No valid watch dirs found, disabling service")
        self._observer.start()

    def on_created(self, event):
        """ Handle a new torrent file being saved to the watch directory

        :param event: File creation event
        :type event: FileCreatedEvent
        """
        if event.src_path.lower().endswith(".torrent"):
            log.info("Got new torrent file save event")
            torrent_name = splitext(basename(event.src_path))[0]
            dir_path = dirname(event.src_path)
            try:
                section = self._path_sections[dir_path]
            except KeyError:
                log.error("Unknown watch path detected: {0}".format(dir_path))
                return False
            else:
                dl_path = config.get_download_path("section_{}".format(section), torrent_name)
                torrent_data = release.TorrentData(torrent_name, open(event.src_path).read(), section)
                self._service_manager.add(torrent_data, self, dl_path=dl_path)

    def stop(self):
        self._observer.stop()
        self._observer.join()
