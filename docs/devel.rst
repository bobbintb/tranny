Developer Guide
===============

A number of different tools are used to develop with. The most complicated setup
is in regards to the web tool set used, built around grunt and sass. The python stuff
is very simple and easy to get running with PIP.

Python Setup
------------

Its highly recommended you develop under a virtualenv, so this is the only method i will
describe.

We require python 2.7 currently, so if you do not have this please install it. You do
not need to install it system wide, nor should you. The setup for this is outside the scope
of this doc so please refer to external docs for this. I do however recommend just
installing it to a custom directory using ./configure --prefix=/home/user/python/2.7 or
something similar. Be sure to reference that specific python executable when running
any commands.

If you do not have virtualenv installed please do so. If you just built python 2.7 then
you will want to install it. Here are the projects `instructions <http://virtualenv.readthedocs.org/en/latest/virtualenv.html>`_
on how to do this.

With that installed we can go ahead and create our virtualenv::

    $ cd $project_root
    $ /path/to/python2.7 virtualenv virtenv

This will install it under virtenv, but you can name this whatever you want. We can now
activate the virtualenv using the activate script. This will make the virtualenv python
the default python used while under that shell.::

    $ source virtenv/bin/activate

We can now install all of the standard python dependencies and well as the developer dependencies since this
is the dev guide::

    $ pip install -r requirements.txt
    $ pip install -r requirements-devel.txt

You should now be good to go if there was no problems.

Web Development Setup
---------------------

In short you will need the following tools installed before continuing, the installation
process for these is out of scope for this, so you should read their respective docs
on how to get them installed correctly:

- `ruby <https://www.ruby-lang.org/>`_
- `nodejs <http://nodejs.org/>`_


Basic steps on linux (# denoting root or sudo command)::

    # npm install -g bower grunt-cli
    $ gem install foundation

With all of the base tools installed we can pull in our JS dependencies using bower::

    $ bower install --config.directory=tranny/static/vendor

Now we will install the grunt tasks that we take advantage of::

    $ npm install grunt-contrib-concat --save-dev
    $ npm install grunt-contrib-coffee --save-dev
    $ npm install grunt-contrib-uglify --save-dev
    $ npm install grunt-contrib-cssmin --save-dev

If that all completed successfully you should be able to run the following with
a similar result, notably the last line.::

    $ grunt build
    Running "sass:dist" (sass) task
    File "tranny/static/css/app.css" created.

    Running "coffee:compileWithMaps" (coffee) task
    >> 1 files created.
    >> 1 source map files created.

    Running "concat:dist" (concat) task
    File tranny/static/js/vendor.js created.

    Done, without errors.

If that was successful you should be good to go and can now use the default grunt task
which will watch for changes in your files and recompile them on each save.::

    $ grunt
    Running "sass:dist" (sass) task
    File "tranny/static/css/app.css" created.

    Running "coffee:compileWithMaps" (coffee) task
    >> 1 files created.
    >> 1 source map files created.

    Running "concat:dist" (concat) task
    File tranny/static/js/vendor.js created.

    Running "watch" task
    Waiting...


For a basic video guide on doing this, please see the zurb foundation
demonstration `video <http://foundation.zurb.com/learn/video-started-with-foundation.html>`_.

Problems
~~~~~~~~

There is an issue with libsass as it does not support sass 3.4 yet. If you receive this error when trying
to build the project you must make a small change::

    Warning: tranny/static/vendor/foundation/scss/foundation/functions:13: error: error reading values after )
    Use --force to continue.

To fix this go to line 13 of tranny/static/vendor/foundation/scss/foundation/functions and remove
the !global declaration so it looks like this::

    $modules: append($modules, $name);


Building Release Versions
-------------------------

todo

Testing
-------

When running unit tests there are 2 environment variables used to configure what
is tested and loaded. By setting ``TEST=`` you will load the test configuration
in the fixtures folder. There are additional values used to flag the testing of specific
clients since we do not currently test them all and do not mock everything yet.

    TEST_TRANSMISSION=1/0
    TEST_DELUGE=1/0
    TEST_RTORRENT=1/0
    TEST_QBITTORRENT=1/0
    TEST_UTORRENT=1/0
