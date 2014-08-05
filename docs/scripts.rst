Management Scripts
------------------

There are several scripts beyond the main application which provide some
extra convience for performing some tasks via the command line. Most of the
scripts live under the scripts path of the source tree with the exception of
`manage.py`. These scripts will all attempt to load the global config `tranny.ini`
before executing, so you can expect those values to be available when executing.

manage.py
~~~~~~~~~

This script proves 2 main functions. Initial configuration of the application and
running the application.

- `manage.py initdb` Drop the databased tables, if they exist, and reinitialize it, creating a new admin user in the process.
- `manage.py run` Load and run the application from the command line, this does not fork the process into the background.


tranny-add.py
~~~~~~~~~~~~~

This script will attempt to load the files passed into it as arguments into the
configured torrent client. The client it uses is determined by the `tranny.ini`
client value. The script will accept 1 or more paths to torrent files, an example of
loading 2 files is below. ::

    ./tranny-add.py The.Torent.Name.2012.S01E01.HDTV.x264-GRP.torrent The.Other.Name.2012.x264-GRP.torrent
    > Connected to rTorrent 0.9.3/0.13.3
    -> The.Torent.Name.2012.S01E01.HDTV.x264-GRP @ 376.2MB
    --> Upload successful
    -> The.Other.Name.2012.x264-GRP @ 2356.3MB
    --> Upload successful

