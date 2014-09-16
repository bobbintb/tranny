Tranny Setup Info
-----------------

This documents outlines setting up the tranny process to start on boot as well as
configuring different services to fetch from.

Requirements
~~~~~~~~~~~~

One of the following torrent clients configured for remote API access

- `deluge <http://deluge-torrent.org>_ ` This is currently the only client that will function with webui capabilities
- `rTorrent <http://rakshasa.github.io/rtorrent/>`_ (scgi) (Partial support)
- `Transmission <http://www.transmissionbt.com/>`_ (jsonrpc) (Not recommended yet)
- `uTorrent 3.x <http://www.utorrent.com/>`_ (webui) (Not recommended yet)

Along with a python distribution and required python libraries

- `Python 2.7 <http://www.python.org/download/>`_ - Python 3 support will come with python 3 gevent support
- `watchdog <https://pypi.python.org/pypi/watchdog>`_
- `transmissionrpc <https://bitbucket.org/blueluna/transmissionrpc/wiki/Home>`_
- `requests <http://docs.python-requests.org/en/latest/>`_
- `feedparser <https://code.google.com/p/feedparser/>`_
- `jsonrpclib <https://github.com/joshmarshall/jsonrpclib>`_

Setup
~~~~~

Its recommended to use a virtualenv to install if possible. Ill outline how to install
using it below.

Checkout the sources::

    $ git clone git://github.com/leighmacdonald/tranny.git
    $ cd tranny

Unix System Prep
~~~~~~~~~~~~~~~~

If you are using a Unix like system (linux,osx,bsd,solaris) you should use these steps, for windows users
please see below.

Install virtualenv with your package manager if its not already installed. Install the
dependencies using pip and the dependencies which are listed under the requirements.txt file.::

    $ virtualenv virtenv # Create virtualenv for tranny
    $ source virtenv/bin/activate # Activate new interpreter on your path
    $ pip install -r requirements.txt # Install required dependencies

Windows System Prep
~~~~~~~~~~~~~~~~~~~

Below are links to installers for some of the libraries required. Make sure you choose the
correct one for your python version. Sticking with CPython 2.7 would be considered best for now.

- `distribute <http://www.lfd.uci.edu/~gohlke/pythonlibs/#distribute>`_
- `pip <http://www.lfd.uci.edu/~gohlke/pythonlibs/#pip>`_
- `psutil <http://www.lfd.uci.edu/~gohlke/pythonlibs/#psutil>`_

The following libraries are installed using pip as they are not available from the site above. You can
install them like so: `pip install package_name`

- `six <https://pypi.python.org/pypi/six>`_
- `pathtools <http://pythonhosted.org/pathtools/>`_

A precompiled installer for pyimdb 32bit python 2.7.
- `imdbpy <http://iweb.dl.sourceforge.net/project/imdbpy/IMDbPY/4.9/IMDbPY-win32-py2.7-4.9.exe>`_

Common configuration setup
~~~~~~~~~~~~~~~~~~~~~~~~~~

Create your own config based on the example provided and rename it to `tranny.ini`. We will
also put this in the users config directory under ~/.config/tranny

    $ mkdir ~/.config/tranny
    $ cp tranny_dist.ini ~/.config/tranny/tranny.ini

From this point you will want to take a moment and setup your configuration file. You should enable
all the services you want to now. For more info check out the following setup doc pages:

- :doc:`services` Service configuration [imdb, trakt, tmdb, etc]

- :doc:`notifications`

Using the editor of your choice, configure any options desired in your new configuration.

    $ vim tranny.ini

Once you have configured your configuration file as desired, notable making sure the database uri
is specified properly you can then initialize a blank database schema. There are 3 optional parameters
that you can also set if you desire. -u/-p will set the credentials for the admin user. This is currently
only used for the optional web ui. If you do not specify then default values of admin/tranny will be used
for the user/password. -w If specified will wipe all existing tables and data from your database. This is not
recoverable so be sure to do it only if you need to.

    $ python tranny-cli.py db_init [-u admin_username] [-p admin_password] [-w wipe existing database]
    2014-09-16 01:32:32,338 - Initialized db schema successfully
    2014-09-16 01:32:32,363 - Created admin user successfully

You can now start the daemon process like so.

    $ python tranny-cli.py run

If you are having issues you can also run the application with debugging log level as well as follows:

    $ python tranny-cli.py -l DEBUG run

I recommend running it like this for a while so you can monitor it for any issues that
arise. Once you are confident in how its working you can proceed to enable it to start
automatically at boot as a daemon.

Auto Start On Boot
~~~~~~~~~~~~~~~~~~

There are a plethora of ways to install the service to run at boot time. These however
are implemented quite a bit different across platforms so be warned, I only test on Linux
currently. If you have success on other platforms please submit a pull request for this
document with the relevant steps required outlined or even just a note telling me of the
status.

Linux (supervisord)
~~~~~~~~~~~~~~~~~~~

This is the easiest method, mostly because its the method most tested with. You will of
course need to install the `supervisor <http://supervisord.org/>`_ daemon and make sure
its enable to start at system boot.

Below is a sample configuration file that should be customized according to your setup. Save
the file as `/etc/supervisor.d/tranny.ini` or append this config to the standard
`/etc/supervisord.conf` file::

    [program:tranny]
    command=/home/user/tranny/virtenv/bin/python /home/user/tranny/tranny-cli.py run
    directory=/home/user/tranny
    stdout_logfile=/home/user/.config/tranny/tranny-supervisor.log
    redirect_stderr=true
    user=user

Windows
~~~~~~~

Who knows... but [this](http://stackoverflow.com/questions/32404/is-it-possible-to-run-a-python-script-as-a-service-in-windows-if-possible-how)
can probably help you get started. Please let me know if you have success.
