Tranny Setup Info
-----------------

This documents outlines setting up the tranny process to start on boot as well as
configuring different services to fetch from.

Requirements
~~~~~~~~~~~~

One of the following torrent clients configured for remote API access

- `rTorrent <http://rakshasa.github.io/rtorrent/>`_ (scgi)
- `Transmission <http://www.transmissionbt.com/>`_ (jsonrpc)
- `uTorrent 3.x <http://www.utorrent.com/>`_ (webui)

Along with a python distribution and required python libraries

- `Python 2.7 <http://www.python.org/download/>`_ - If you do not use the directory watch feature, it will probably run on python3 as well. The libraries below are all required. The pip installer will take care of installing them if you are using a virtualenv though.
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

Create your own config based of the example provided and rename it to `tranny.ini`.

    $ cp tranny_dist.ini tranny.ini

From this point you will want to take a moment and setup your configuration file. You should enable
all the services you want to now. For more info check out the following setup doc pages:

- :doc:`config_service_rss`

- :doc:`config_service_btn`

Using the editor of your choice, configure any options desired in your new configuration.

    $ vim tranny.ini

You can now start the daemon process like so.

    $ python tranny-daemon.py

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
course need to install the [supervisor](http://supervisord.org/) daemon and make sure
its enable to start at system boot.

Below is a sample configuration file that should be customized according to your setup. Save
the file as `/etc/supervisor.d/tranny.ini` or append this config to the standard
`/etc/supervisord.conf` file::

    [program:tranny]
    command=/home/user/tranny/virtenv/bin/python /home/user/tranny/tranny-daemon.py
    directory=/home/user/tranny
    stdout_logfile=/home/user/tranny/tranny-supervisor.log
    redirect_stderr=true
    user=user

Windows
~~~~~~~

todo
