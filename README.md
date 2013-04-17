# tranny - A highly configurable torrent client/api wrapper

Tranny is a python library and daemon designed to interact with torrent client via their respective
API's. Currently support is limited to the [transmission](http://www.transmissionbt.com/) client, however
plans exist to expand this to at least [rtorrent](http://libtorrent.rakshasa.no/), and possibly
[deluge](http://deluge-torrent.org/).

## Design Goal

This tool will attempt to automate repetative downloading tasks as efficiently as possible. This
means that there will be support for loading clients from many different sources without loading
any duplicates.

## Implemented Features

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
- Easily extendable service providers to allow for custom providers to be used

## Setup

For more in depth ways to start the service please see the [setup docs](docs/setup.md).

## Services Available

Each site has its own method of provided updated release information. Tranny aims to
support as many as possible. Outlined below is the current state of backend service
providers and torrent sites which are supported.

- generic - Fetch releases over RSS (revtt,scc,tl,etc...)
- [BTN](https://broadcasthe.net) - Accesses the site over their [JSON-RPC API](http://btnapps.net/docs.php)

## Planned Features

These are the features i am planning to implement. If you have features you would like to see implemented
please dont hesitate to contact me.

- Alternate torrent client support
    - [rTorrent](http://libtorrent.rakshasa.no/)
    - [deluge](http://deluge-torrent.org/)
- IRC service providers
    - Simple internal IRC client
    - IRC Client scripts to interface with tranny
        - [weechat](http://www.weechat.org/)
        - [irssi](http://www.irssi.org/)
        - [mIRC](http://www.mirc.com/)
- RDBMS datastore backend
    - [postgres](http://www.postgresql.org/)
    - [MySQL](http://www.mysql.com/)

## Possible Features

- User interfaces:
    - Simple WebUI
    - Simple QT Interface
