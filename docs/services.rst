External Services
=================

External/3rd party API's used to fetch metadata for media

IMDB
----

SQL Mode
~~~~~~~~

You can optionally import the entire imdb into a local databse for faster lookup
times.::

    $ tranny-cli.py imdb

Using SQLite on a very fast machine with SSD's this took about 30 minutes to complete. Other databases are
likely to be considerably slower than this. For reference i have seen postgres take 2 days with a default
configuration.

Once complete the config flag for sql must be set to true::

    [service_imdb]
    enabled = true
    sql = true

If using postgresql there are some parameters you can tune in the database to speed up this load
time.::

    fsync = off
    full_page_writes = off

For more information on speeding up postgresql's insertion speed see `this <http://stackoverflow.com/questions/9407442/optimise-postgresql-for-fast-testing>`_ post.

