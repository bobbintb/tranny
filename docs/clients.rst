Torrent Client Configuration
============================

Examples of how to setup backend torrent clients for use with tranny.

The most feature complete client is deluge so it is the recommended choice for now.

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

To allow connections to deluge you must enable the WebUI plugin. Additionally the default settings
disallow remote connections. Change the "allow_remote" setting in $HOME/.config/deluge/core.conf::

    "allow_remote": true

:ref:`deluge_api`

UTorrent
--------

Support coming soon

Transmission
------------

For tranny to be able to communicate with the transmission client you must enable remove access.
You can find this in the ``preferences -> remote`` menu of the client.

If you are accessing the client from a remote connection, as in your client is not on the
same computer as tranny, you must enable the rpc-whitelist for your ip::

    "rpc-whitelist": "127.0.0.1,192.168.10.*,10.0.0.*",
    "rpc-whitelist-enabled": true,

You can set this in transmissions settings.json
