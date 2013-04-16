# tranny - A highly configurable torrent client/api wrapper

Tranny is a python library and daemon designed to interact with torrent client via their respective
API's. Currently support is limited to the [transmission](http://www.transmissionbt.com/) client, however
plans exist to expand this to at least [rtorrent](http://libtorrent.rakshasa.no/), and possibly
[deluge](http://deluge-torrent.org/).

## Design Goal

This tool will attempt to automate repetative downloading tasks as efficiently as possible. This
means that there will be support for loading clients from many different sources without loading
any duplicates.

## Features

- Support for transmission daemon
- Auto sorting of releases into the correct destination folders based on the name of the torrent. For example
when downloading a TV episode, it will be placed in the configured TV download path automatically.
- TV sorting/grouping. Different episodes of a TV show can be grouped under 1 common sub directory of the
download path automcatilly. eg. Show.Name.S01E12.720p.HDTV.x264-FiHTV -> /download/path/tv/Show.Name/Show.Name.S01E12.720p.HDTV.x264-FiHTV
- Only download the first matching torrent from whichever source finds it first, skipping subsequent duplicate
matches.
- Support for handling "Proper" releases
- Global ignore patterns
- Tested only on linux currently, however it should work equally well on osx/bsd/win. Please let me know.
- Unlimited number of watch folders which can individually be configured with their own section
- Downloading over any number of RSS feeds
    - Each Feed is able to have custom settings applied such as minimum refresh intervals.
- Persistent download history

## Requirements

- [Python 2.6/2.7](http://www.python.org/download/) - If you do not use the directory watch feature, it will
probably run on python3 as well.
- [Transmission](http://www.transmissionbt.com/)
- [watchdog](https://pypi.python.org/pypi/watchdog)
- [transmissionrpc](https://bitbucket.org/blueluna/transmissionrpc/wiki/Home)
- [requests](http://docs.python-requests.org/en/latest/)
- [feedparser](https://code.google.com/p/feedparser/)

## Setup

Its recommeneded to use a virtualenv to install if possible. Ill outline its usable below.

    $ git clone git://github.com/leighmacdonald/tranny.git
    $ cd tranny
    $ virtualenv virtenv
    $ source virtenv/bin/activate
    $ pip install -r requirements.txt
    $ cp tranny_dist.ini tranny.ini

From this point you will want to take a moment and setup your configuration file.

    $ vim tranny.ini

You can now start the daemon process like so

    $ python tranny-daemon.py


## Planned Features

- Alternate torrent client support
    - [rTorrent](http://libtorrent.rakshasa.no/)
    - [deluge](http://deluge-torrent.org/)
- IRC download sources
    - Simple internal IRC client
    - IRC Client scripts to interface with tranny
        - [weechat](http://www.weechat.org/)
        - [irssi](http://www.irssi.org/)
        - [mIRC](http://www.mirc.com/)
- RDBMS datastore backend
    - [postgres]()
    - [MySQL](http://www.mysql.com/)



## Possible Features

- User interfaces:
    - Simple WebUI
    - Simple QT Interface
