# -*- coding: utf-8 -*-
"""
Basic class which emulates basic components of a torrent client, but just writes out
torrent files to a configured directory. This can be used for example to output
the files to a non-supported torrent clients watch folder for at least some
basic type of integration support
"""
from __future__ import unicode_literals, absolute_import, with_statement
from os.path import exists, expanduser, join, isdir
from tranny import client
from tranny.util import mkdirp


class SimpleFileClient(client.TorrentClient):
    """
    Simple file based client
    """

    # Configuration file section name
    config_key = "client_simplefile"

    def __init__(self, directory=None):
        """
        """
        super(SimpleFileClient, self).__init__()
        directory = expanduser(directory)
        if exists(directory):
            if not isdir(directory):
                raise OSError("File output path is not a directory: {}".format(directory))
        else:
            mkdirp(directory)
        self.directory = directory

    def add(self, data, download_dir=None):
        """
        :param data: Torrent data to load in
        :type data: TorrentData
        :param download_dir: This is ignored for this client
        :type download_dir: basestring
        :return: Status of successful load (according to deluge)
        :rtype: bool
        """
        if data.release_name.lower().endswith(".torrent"):
            file_name = data.release_name
        else:
            file_name = "{}.torrent".format(data.release_name)
        out_file = join(self.directory, file_name)
        with open(out_file, 'wb') as t:
            t.write(data.torrent_data)
        self.log.info("Wrote torrent to file: {}".format(out_file))
        return True

    def client_version(self):
        return "SimpleFile, 0.1"

    def torrent_add(self, data, download_dir=None):
        pass

    def current_speeds(self):
        return 0.0, 0.0

    def torrent_list(self):
        """ Return empty list since we are not real """
        return []

    def torrent_status(self, info_hash):
        return {}

    def torrent_pause(self, info_hash):
        return True

    def torrent_start(self, info_hash):
        return True

    def torrent_remove(self, info_hash, remove_data=False):
        return True

    def torrent_reannounce(self, info_hash):
        return True

    def torrent_recheck(self, info_hash):
        return True

    def torrent_files(self, info_hash):
        return []

    def torrent_peers(self, info_hash):
        return []

    def disconnect(self):
        return True

    def get_events(self):
        return []

    def torrent_queue_top(self, info_hash):
        return True

    def torrent_queue_bottom(self, info_hash):
        return True

    def torrent_move_data(self, info_hash, dest):
        return True

    def torrent_queue_up(self, info_hash):
        return True

    def torrent_queue_down(self, info_hash):
        return True
