#!/bin/env python
# -*- coding: utf-8 -*-
"""
Basic CLI script to manually upload a torrent to the configured backend client

./tranny-add torrent1.torrent torrent2.torrent..

"""
from __future__ import unicode_literals
from os.path import dirname
from sys import argv, path

path.append(dirname(dirname(__file__)))

from tranny.exceptions import ConfigError
from tranny.client import init_client
from tranny.torrent import Torrent

client = init_client()

print("> Connected to {}".format(client))
try:
    if len(argv) <= 1:
        raise ConfigError("! Not enough arguments")
    torrent_data = []
    for torrent in argv[1:]:
        try:
            torrent_data.append(open(torrent, 'r').read())
        except IOError as err:
            print(err)
    if len(torrent_data) != len(argv[1:]):
        raise ConfigError("! Failed to locate all files, bailing")
except (ConfigError, Exception) as err:
    print(err)
else:
    for raw_torrent in torrent_data:
        torrent_struct = Torrent.from_str(raw_torrent)
        print("-> {} @ {}".format(torrent_struct['info']['name'], torrent_struct.size(human=True)))
        if client.add(raw_torrent):
            print("--> Upload successful")
        else:
            print("--> Upload failed")

