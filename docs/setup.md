# Tranny Setup Info

This documents outlines setting up the tranny process to start on boot as well as
configuring different services to fetch from.

## Requirements

- [Transmission](http://www.transmissionbt.com/)
- [Python 2.6/2.7](http://www.python.org/download/) - If you do not use the directory watch feature, it will
probably run on python3 as well. The libraries below are all required. The pip installer will
 take care of installing them if you are using a virtualenv though.
    - [watchdog](https://pypi.python.org/pypi/watchdog)
    - [transmissionrpc](https://bitbucket.org/blueluna/transmissionrpc/wiki/Home)
    - [requests](http://docs.python-requests.org/en/latest/)
    - [feedparser](https://code.google.com/p/feedparser/)
    - [jsonrpclib](https://github.com/joshmarshall/jsonrpclib)

## Setup

Its recommeneded to use a virtualenv to install if possible. Ill outline how to install
using it below.

Checkout the sources

    $ git clone git://github.com/leighmacdonald/tranny.git
    $ cd tranny

Setup virtualenv and install the dependencied using pip for the application

    $ virtualenv virtenv
    $ source virtenv/bin/activate
    $ pip install -r requirements.txt

Create your own config based of the example provided

    $ cp tranny_dist.ini tranny.ini

From this point you will want to take a moment and setup your configuration file. You should enable
all the services you want to now. For more info check out the following setup doc pages:

    - [RSS Setup](docs/config_rss.md)
    - [BTN API](docs/config_service_btn.md)

    $ $EDITOR tranny.ini

You can now start the daemon process like so

    $ python tranny-daemon.py

## Auto Start On Boot

There are a plethora of ways to install the service to run at boot time. These however
are implemented quite a bit different across platforms so be warned, I only test on Linux
currently. If you have success on other platforms please submit a pull request for this
document with the relevant steps required outlined or even just a note telling me of the
status.

### Linux (supervisord)

This is the easiest method, mostly because its the method most tested with. You will of
course need to install the [supervisor](http://supervisord.org/) daemon and make sure
its enable to start at system boot.

Below is a sample configuration file that should be customized according to your setup. Save
the file as `/etc/supervisor.d/tranny.ini` or append this config to the standard
`/etc/supervisord.conf` file.

    [program:tranny]
    command=/home/user/tranny/virtenv/bin/python /home/user/tranny/tranny-daemon.py
    directory=/home/user/tranny
    stdout_logfile=/home/user/tranny/tranny-supervisor.log
    redirect_stderr=true
    user=user

