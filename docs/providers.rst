Providers
=========

Providers are considered to be modules that allow fetching release lists from remote sources
as well as downloading from the sources. This includes common stuff like RSS and API based
services, but can be extended to support anything that can provide that type of
information

BTN API Provider
----------------

BTN provides its own API over JSON-RPC. It requires a API key which can be obtained
from going to your profile and clicking the API tab. If you do not already have a key, you
can create a new API key, otherwise use your existing one.

Below is a full set of configuration values which are used for the service. You should
only need to update the api_token to have a working service.::

    [provider_broadcastthenet]
    enabled = true
    url = http://api.btnapps.net/
    interval = 150
    ; 32 character API Key.
    api_token = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

Be aware that BTN has an API rate limit of 150req/s so do not set your interval too low. If you
want data faster than this, you should be using an IRC bot instead as it is event based and
will get notified immediately of a new release.

RSS Feed Provider
-----------------

Tranny supports downloading over RSS feeds. You can add as many sections as you would like::

    [rss_name]
    url = http://rss.torrensite.org/
    enabled = true
    interval = 300

You should be careful not to set your interval too low. Most sites really do not like less
than 300 seconds (5min) and you may get banned or run into rate limit issues if you
do not respect that.


PTP Provider
------------

This is currently not 100% implemented and should not be used yet.


HDBits Provider
---------------

This is currently not 100% implemented and should not be used yet. Also keep in mind
that HDBits is not all that keen on scripts being used to download from them.
