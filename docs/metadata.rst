Metadata Services
-----------------

IMDB (HTTP)
~~~~~~~~~~~

.. note:: As of version 5 of the IMDBpy library this step is no longer necessary and it will
    work as expected from the official sources which should automatically be installed.
    If you are stuck with 4.x for some reason, then you will need to install a current version
    similar to how is outlined below.

As of 17/04/2013, the IMDBpy library does not work with the current IMDB site. To enable
usage of IMDB you must install a development version of the library. You will need
`mercurial <http://mercurial.selenic.com/>`_ installed to download the source tree. Below
is a step by step example of installing the library.::

    $ cd tranny
    $ source virtenv/bin/activate
    $ hg clone ssh://hg@bitbucket.org/alberanid/imdbpy
    $ cd imdbpy
    $ python setup.py install


IMDB (SQL)
~~~~~~~~~~

Setup for this has been automated so it will download and install the database for you.
This will auto create the tables and populate them for you automatically in the
sqlalchemy URI that you have defined in your config.::

    $ python tranny-cli.py imdb

.. warning:: This process can take a *VERY* long time to complete depending on your
    hardware and database used. If you are using anything but SQLite this can take more
    than 24 hours to complete on fairly good hardware, even with an SSD. Below i will show
    some times its taken me when testing to do this. If you have more data points please
    send them to me or add them and create a pull request.

    - SQLite ~35mins (i5-3470/Samsung Pro SSD/32gb)
    - Postgresql 9.3.5 30hrs (conf: fsync=off) (i5-3470/Samsung Pro SSD/32gb)

Once you have completed your import, you must change your config to show sql = true.::

    [service_imdb]
    enabled = true
    sql = true

You will probably want to run this every so often to keep things current with the live imdb
site by using a cron job of some sort. I wouldn't recommend doing this every day, but once a week
for sqlite is probably ok, once every couple weeks to a month for postgres.

themoviedb.org
~~~~~~~~~~~~~~

To use themoviedb info, you must `register <https://www.themoviedb.org/account/signup>`_ and create an API key.
Once you have the API key you can add it to your tranny.ini as follows:::

    [themoviedb]
    api_key = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

.. note::
    This module is not really used at the moment and may be removed if it doesnt offer
    enough over the others.
