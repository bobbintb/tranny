# tranny - A highly configurable torrent client/api wrapper

Tranny is a python library and daemon designed to interact with torrent client via their respective
API's. Currently support is limited to the [transmission](http://www.transmissionbt.com/) client, however
plans exist to expand this to at least [rtorrent](http://libtorrent.rakshasa.no/), and possibly
[deluge](http://deluge-torrent.org/).

## Design Goal

This tool will attempt to automate repetative downloading tasks as efficiently as possible. This
means that there will be support for loading clients from many different sources without loading
any duplicates.

## Features Status

    Key | Meaning
    ----+---------------------------
     x  | Feature Completed
     ~  | Feature In-Progress
     u  | Untested but may work
     _  | Planned

**Torrent clients**

- [x] [rTorrent](https://github.com/rakshasa/rtorrent)
- [x] [Transmission](http://www.transmissionbt.com/)
- [_] [deluge](http://deluge-torrent.org/)
- [~] [uTorrent](http://www.utorrent.com/)
- [_] [qBittorent](http://www.qbittorrent.org/)


**Auto Sorting & Downloading**

- [x] Auto sorting of releases into the correct destination folders based on the name of the torrent. For example
when downloading a TV episode, it will be placed in the configured TV download path automatically.
- [x] TV sorting/grouping. Different episodes of a TV show can be grouped under 1 common sub directory of the
download path automcatilly. eg. Show.Name.S01E12.720p.HDTV.x264-FiHTV -> /download/path/tv/Show.Name/Show.Name.S01E12.720p.HDTV.x264-FiHTV
- [x] Only download the first matching torrent from whichever source finds it first, skipping subsequent duplicate
matches.
- [x] Support for handling "Proper" releases
- [x] Global ignore patterns
- [x] Persistent download history
- [~] Handle daily broadcast shows properly
- [_] Custom regex matching

**Torrent Source Service Providers**

- [x] Watch folders (Unlimited number of watch folders which can individually be configured with their own section)
- [x] RSS Feeds (Parsing any number of feeds supported. Independent settings such as different intervals per feed.)
- [_] RSS Feed HTTP Auth
- [x] BTN API ([JSON-RPC API](http://btnapps.net/docs.php))
- [_] Internal IRC client
- [_] [weechat](http://www.weechat.org/)
- [_] [irssi](http://www.irssi.org/)
- [_] [mIRC](http://www.mirc.com/)

**OS Support**

- [x] Linux (Tested only on linux currently)
- [u] Windows (may work with some features not available)
- [u] OSX (may work with some features not available)


- Easily extendable service providers to allow for custom providers to be used

**RDBMS datastore backend**

- [x] [SQLite](http://www.sqlite.org/)
- [x] [postgres](http://www.postgresql.org/)
- [u] Most (all?) other [dialects](http://docs.sqlalchemy.org/en/rel_0_8/dialects/) supported by sqlalchemy
should work, notably [MySQL](http://www.mysql.com/), but are untested.

## Setup

For more in depth ways to start the service please see the [setup docs](docs/setup.md).
