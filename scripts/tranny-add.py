#!/bin/env python
# -*- coding: utf-8 -*-
"""
Basic CLI script to manually upload a torrent to the configured backend client

./tranny-add torrent1.torrent torrent2.torrent..

"""

from os.path import dirname
from sys import argv, path, exit

# silly hack for development purposes
path.append(dirname(dirname(__file__)))

from tranny.exceptions import ConfigError
from tranny.client import init_client
from tranny.torrent import Torrent


def add_torrents_from_cli(args):
    """ Parse command line args and try to load torrent files found

    :param args:
    :type args:
    :return:
    :rtype:
    """
    try:
        if len(args) <= 1:
            raise ConfigError("! Not enough arguments")

        torrent_data = []
        for torrent in args[1:]:
            try:
                torrent_data.append(open(torrent, 'r').read())
            except IOError as err:
                pass
        if len(torrent_data) != len(args[1:]):
            raise ConfigError("! Failed to locate any files")
    except (ConfigError, Exception) as err:
        print(err)
        return 1
    else:
        if torrent_data:
            client = init_client()
            print(("> Connected to {}".format(client)))
            for raw_torrent in torrent_data:
                torrent_struct = Torrent.from_str(raw_torrent)
                print(("-> {} @ {}".format(torrent_struct['info']['name'].decode('utf8'), torrent_struct.size(human=True))))
                if client.add(raw_torrent):
                    print("--> Upload successful")
                    return 0
                else:
                    print("--> Upload failed")
                    return 1

if __name__ == "__main__":
    exit(add_torrents_from_cli(argv))
