External Services
=================

External/3rd party API's used to fetch metadata for media

IMDB
----

SQL Mode
~~~~~~~~

You can optionally import the entire imdb into a local databse for faster lookup
times.

    $ tranny-cli.py imdb

Using SQLite on a very fast machine with SSD's this took about 30 minutes to complete. Other databases are
likely to be considerably slower than this.

Once complete the config flag for sql must be set to true:

    [service_imdb]
    enabled = true
    sql = true

