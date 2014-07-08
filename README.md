# Tranny - A highly configurable torrent downloader and API wrapper

Tranny is a python library and daemon designed to interact with torrent client via their respective
API's. Currently support is limited to the [transmission](http://www.transmissionbt.com/) client, however
plans exist to expand this to at least [rtorrent](http://libtorrent.rakshasa.no/), and possibly
[deluge](http://deluge-torrent.org/).

## Design Goal

This tool will attempt to automate repetitive downloading tasks as efficiently as possible. This
means that there will be support for loading clients from many different sources without loading
any duplicates.

## Features Status

**Torrent clients**

- [x] [rTorrent](https://github.com/rakshasa/rtorrent)
- [x] [Transmission](http://www.transmissionbt.com/)
- [ ] [deluge](http://deluge-torrent.org/)
- [ ] [uTorrent](http://www.utorrent.com/)
- [ ] [qBittorent](http://www.qbittorrent.org/)


**Auto Sorting & Downloading**

- [x] Auto sorting of releases into the correct destination folders based on the name of the torrent. For example
when downloading a TV episode, it will be placed in the configured TV download path automatically.
- [x] TV sorting/grouping. Different episodes of a TV show can be grouped under 1 common sub directory of the
download path automatically. eg. Show.Name.S01E12.720p.HDTV.x264-FiHTV -> /download/path/tv/Show.Name/Show.Name.S01E12.720p.HDTV.x264-FiHTV
- [x] Only download the first matching torrent from whichever source finds it first, skipping subsequent duplicate
matches.
- [x] Support for handling "Proper" releases
- [x] Global ignore patterns
- [ ] Persistent download history
- [ ] Handle daily broadcast shows properly
- [ ] Custom regex matching
- [ ] Filter to only accept private torrents
- [ ] Skip releases that don't have a minimum [iMDB](http://imdb.com) score
- [ ] Skip releases that don't have a minimum [The Movie DB](http://themoviedb.org) score
- [ ] Skip releases which are older than N pre time.
- [ ] Skip releases which are not available under predb (Usually P2P)
- [ ] Check for disk space available and set a minimum disk space buffer to provide

**Notifications**
- [ ] IRC
- [ ] XMPP/Jabber
- [ ] Email
- [ ] SMS

**Service Providers**

- [x] Watch folders (Unlimited number of watch folders which can individually be configured with their own section)
- [x] RSS Feeds (Parsing any number of feeds supported. Independent settings such as different intervals per feed.)
- [ ] RSS Feed HTTP Auth
- [x] BTN API ([JSON-RPC API](http://btnapps.net/docs.php))
- [ ] Internal IRC client
- [ ] [weechat](http://www.weechat.org/)
- [ ] [irssi](http://www.irssi.org/)
- [ ] [mIRC](http://www.mirc.com/)
- [ ] IRC PreDB scraper support

**OS Support**

- [x] Linux (Tested only on linux currently)
- [ ] Windows (may work with some features not available)
- [ ] OSX (may work with some features not available)

**RDBMS datastore backend**

- [x] [SQLite](http://www.sqlite.org/) Default, built-in to python generally by default.
- [x] [postgres](http://www.postgresql.org/)
- [ ] Most (all?) other [dialects](http://docs.sqlalchemy.org/en/rel_0_8/dialects/) supported by sqlalchemy
should work, notably [MySQL](http://www.mysql.com/), but are untested.


**WebUI**

These features are not a major priority for me yet. But in the future they will probably
be. Some of the stuff is beyond the initial scope of the app and will only appear once
ive ironed out other elements. There are decent webui's available elsewhere which complement
trannys feature set without much overlap.

- [x] Web based configuration of most things (Filters / System settings)
- [x] Simple graphs for sources / media types
- [ ] Loaded torrent list view with basic info
- [ ] Torrent detail view (peers/trackers/etc)
- [ ] Start/Stop/Pause torrents
- [ ] Set priorities of individual torrents
- [x] Responsive design for mobile support

**Other**

- [ ] Python 3 support. Tranny itself should be python3 compatible, but some libraries are not.


## Setup

For more in depth ways to start the service please see the [setup docs](docs/setup.md).
