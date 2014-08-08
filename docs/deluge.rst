Torrent Client Configuration
============================

Examples of how to setup backend torrent clients for use with tranny.

rTorrent
--------

The simplest way to make this work is using direct SCGI access, however this method is less secure by default and
should have firewall rules in place to lock it down. The main advantage is using it locally and not needing
to setup a web server to proxy the SCGI request to rTorrent. If you are accessing a remote instance of rTorrent
its probably a better idea to use an actual web server if you are not confident in setting up secure firewall
restrictions.

Deluge (JSON-RPC)
-----------------

More info available at `Deluge JSON-RPC <http://dev.deluge-torrent.org/wiki/Development/DelugeRPC>`_

Deluge (Python)
---------------

Warn: Using this method is unrecommended as its overly complex for little gain over the JSON-RPC version and
may in fact be removed altogether.

If you wish to use the deluge direct client (NOT OVER JSON-RPC) there are some caveats to making it
work properly alongside tranny.

- If you are using a virtualenv to run tranny, select one of the following:

    - Install deluge into your virtualenv directly. This can be a non-trivial task, especially if you are not familiar with python packaging. Its not recommended unless you know what you are doing.

    - Install deluge system wide using your package manager and then install the virtualenv using the `--system-site-packages` flag. This will make it so you inherit the global python packages.

    - Install everything globally and don't use virtualenv at all. This is highly unrecommended.


UTorrent
--------

Support coming soon

Transmission
------------

Support coming soon
