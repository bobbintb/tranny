Ratings & Media Info
--------------------

IMDB
~~~~

As of 17/04/2013, the IMDBpy library does not work with the current IMDB site. To enable
usage of IMDB you must install a development version of the library. You will need
`mercurial <http://mercurial.selenic.com/>`_ installed to download the source tree. Below
is a step by step example of installing the library.::

    $ cd tranny
    $ source virtenv/bin/activate
    $ hg clone ssh://hg@bitbucket.org/alberanid/imdbpy
    $ cd imdbpy
    $ python setup.py install

Downloading The IMDB DB For Local Use
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

todo.


themoviedb.org
~~~~~~~~~~~~~~

To use themoviedb info, you must `register <https://www.themoviedb.org/account/signup>`_ and create an API key.
Once you have the API key you can add it to your tranny.ini as follows:::

    [themoviedb]
    api_key = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

