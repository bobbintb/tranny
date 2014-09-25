# Tranny - A highly configurable torrent downloader and API wrapper


**This is still early in the development process, i don't recommend users commit to using it yet as its still in a constant
state of change.**

Tranny is a python library, daemon and web interface designed to interact with a number of torrent clients via their respective
API's. It shares some goals similar to [sickbeard](http://sickbeard.com/) but is tailored to torrents and
specifically private tracker support. Its very unlikely [usenet/nbz](http://en.wikipedia.org/wiki/NZB) support will
ever be considered as an alternate to torrent backends, so stick to sickbeard if that is your poison of choice.

## Design Goal

This tools primary goal was to attempt to automate repetitive downloading tasks as efficiently as possible. This
means that there will be support for loading torrents from many different sources, hopefully without loading
any duplicates. In addition to this support has expanded to also support a generic torrent webui similar to rtorrent's
[ruTorrent](https://github.com/Novik/ruTorrent) or the built in WebUI plugins for [deluge](http://deluge-torrent.org/) among
others. All of these function essentially in the same manner so supporting all of the different torrent
back-ends relatively easy, similar to the [transdroid](http://www.transdroid.org/) application.

## Features Status

**Torrent clients**

I am primarily developing against the deluge API so it will be the most supported initially and is probably
what you should stick to for now. Once this is stable i will finish polishing the other client support to also
have 1st class support. I am not currently considering any other clients except potentially Vuze/Azuereus if the
demand is there, but its not on my roadmap at all. (Tixati)[http://tixati.com/] may also be considered now that it
has some form of web api, but only when trackers start to generally white list it will i move in that direction.
Alternatively I would also accept pull requests for these 2 clients as long as they are feature complete.

- [ ] [rTorrent](https://github.com/rakshasa/rtorrent) (partial support)
- [ ] [Transmission](http://www.transmissionbt.com/) (partial support)
- [x] [deluge](http://deluge-torrent.org/)
- [ ] [uTorrent](http://www.utorrent.com/)
- [ ] [qBittorent](http://www.qbittorrent.org/) (partial support)


**Auto Sorting & Downloading**

- [x] Auto sorting of releases into the correct destination folders based on the name of the torrent. For example
when downloading a TV episode, it will be placed in the configured TV download path automatically.
- [x] TV sorting/grouping. Different episodes of a TV show can be grouped under 1 common sub directory of the
download path automatically. eg. Show.Name.S01E12.720p.HDTV.x264-FiHTV -> /download/path/tv/Show.Name/Show.Name.S01E12.720p.HDTV.x264-FiHTV
- [x] Only download the first matching torrent from whichever source finds it first, skipping subsequent duplicate
matches.
- [x] Support for handling "Proper" releases
- [x] Global ignore patterns
- [x] Persistent download history
- [x] Minimum/Maximum file size filtering
- [ ] Handle daily broadcast show properties (ex. Delete daily shows over a week old)
- [ ] Custom regex matching
- [ ] Filter to only accept private torrents
- [ ] Skip releases that don't have a minimum [iMDB](http://imdb.com) score
- [ ] Skip releases that don't have a minimum [The Movie DB](http://themoviedb.org) score
- [ ] Skip releases which are older than N pre time.
- [ ] Skip releases which are not available under predb (Usually P2P)
- [ ] Check for disk space available and set a minimum disk space buffer to provide

**Notifications**

The notification features are likely to be the lowest priority at the moment and will only come along in something
like a version 2 of the application. Their support is absolutely planned however.

- [ ] IRC Bot
- [ ] Email
- [ ] SMS
- [ ] Growl


**Service Providers**

These are backend services that are continually updates either by polling, or events broadcasted depending
on the service.

- [x] Watch folders (Unlimited number of watch folders which can individually be configured with their own section)
- [x] RSS Feeds (Parsing any number of feeds supported. Independent settings such as different intervals per feed.)
- [ ] RSS Feed HTTP Auth
- [x] BTN API ([JSON-RPC API](http://btnapps.net/docs.php))
- [ ] Internal IRC client. Functionality similar to [autodl-irssi](http://sourceforge.net/projects/autodl-irssi/)
- [ ] [weechat](http://www.weechat.org/) Python parser script
- [ ] [irssi](http://www.irssi.org/) Probably perl based, python support seems weak
- [ ] [mIRC](http://www.mirc.com/) If someone wants to develop this... :)
- [ ] IRC PreDB scraper support. Using the internal IRC client record pre logs for local lookup

**OS Support**

- [x] Linux (Tested only on linux currently)
- [ ] Windows (may work, untested..)
- [ ] OSX (likely works, untested..)
- [ ] Open/Free/NetBSD (likely works, untested..)

**RDBMS datastore backend**

- [x] [SQLite](http://www.sqlite.org/) Default, built-in to python generally by default.
- [x] [postgres](http://www.postgresql.org/)
- [x] [mysql5+](http://mysql.com)
- [x] [oracle](http://oracle.com)


**WebUI**

This was something i was not originally interested in, but later decided to include as it is a relatively simple
addition with nice rewards for having complete integration with backend services that really make it stand out
as a feature compared to traditional WebUI's/clients. This is not however going to be a required component to use, all
configuration and applications will work without any webui active at all, making this component 100% optional with
the ability to disable it completely.

- [x] Web based configuration of most things (Filters / System settings)
- [x] Simple graphs for sources / media types
- [x] Loaded torrent list view with basic info
- [x] Torrent detail view (peers/trackers/etc)
- [x] Real-time peer stat graphs (clients/origin country)
- [x] Real-time traffic stat graphs (up/dn)
- [x] Start/Stop/Pause torrents
- [ ] Set priorities of individual torrents
- [x] Responsive design for mobile support
- [ ] Right click context menu action support
- [ ] Multi user support (I am unsure how i want to proceed with this, but its something i would like to have)

**Other**

- [ ] Python 3 support. Tranny itself should be python3 compatible, but some libraries are not (gevent).
- [ ] API support


## Libraries used

A list of the major library used.

**Python**

- [gevent](http://www.gevent.org/)
- [feedparser](https://code.google.com/p/feedparser/)
- [Flask](http://flask.pocoo.org/)
- [SQLAlchemy](http://www.sqlalchemy.org/)
- [watchdog](https://github.com/gorakhargosh/watchdog)
- [IMDbPY](http://imdbpy.sourceforge.net/)
- [Jinja2](https://github.com/mitsuhiko/jinja2)
- [Sphinx](http://sphinx-doc.org/)

**Web**

- [Foundation](http://foundation.zurb.com/)
- [Epoch](https://github.com/fastly/epoch)
- [lodash](http://lodash.com/)
- [socketio](http://socket.io/)
- [fontello](http://fontello.com/)


## Setup

For more in depth ways to start the service please see the [setup docs](docs/setup.md).

## Contributing

If you would like to start contributing to the project, please fork it and read the 
[developer guide](http://torrent-tranny.readthedocs.org/en/latest/devel.html) to get started. Contributions are welcomed.



## Contact

I am generally available in the #tranny channel on freenode
