# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

__author__ = "Leigh MacDonald <leigh.macdonald@gmail.com>"
__license__ = "BSD 3-Clause"
__copyright__ = "Copyright (c) 2013-2014 Leigh MacDonald"
__version__ = '0.0.1'

import argparse
import logging


def parse_args():
    def cmd_start(options):
        import gevent
        import signal
        from tranny.manager import ServiceManager

        gevent.signal(signal.SIGQUIT, gevent.kill)

        application = ServiceManager()
        application.start()

    def cmd_db_drop(options):
        from tranny.datastore import db_drop
        db_drop()

    def cmd_db_init(options):
        from tranny.datastore import db_drop, db_init
        db_init(username=options.username, password=options.password, wipe=options.wipe)

    def cmd_cache_clear(options):
        from tranny import cache
        cache.invalidate()

    parser = argparse.ArgumentParser(prog="tranny-cli.py", description="Tranny torrent management system")
    parser.add_argument("-c", "--config", help="Specify alternate config path", default=False)
    parser.add_argument("-l", "--loglevel", help="Set logging level", default=False)

    subparsers = parser.add_subparsers(help="Command help")

    db_init = subparsers.add_parser("db_init", help="Initialize the database schema")
    db_init.add_argument("-u", "--username", help="Admin username", default="admin")
    db_init.add_argument("-p", "--password", help="Admin password", default="tranny")
    db_init.add_argument("-w", "--wipe", help="Wipe any existing database", action="store_true")
    db_init.set_defaults(func=cmd_db_init)

    db_drop = subparsers.add_parser("db_drop", help="Drop (delete) the existing database. This is non-reversible.")
    db_drop.set_defaults(func=cmd_db_drop)

    run = subparsers.add_parser("run", help="Run the application")
    run.add_argument("-H", "--host", help="WebUI host to bind to", default="admin")
    run.add_argument("-P", "--port", help="WebUI port to bind to", default="tranny")
    run.set_defaults(func=cmd_start)

    # aliases=['cc'] (requires 3.2+)
    cache_clear = subparsers.add_parser("cache_clear", help="Clear the application cache")
    cache_clear.set_defaults(func=cmd_cache_clear)

    return parser.parse_args()


def main():
    """ Main entry point for the application. Runs the command parsed from the CLI
    using the argparse func system
    """
    # Exception raised on exit due to threading module loading before gevent
    # This preemptive patching prevents this
    # see: http://stackoverflow.com/questions/8774958/keyerror-in-module-threading-after-a-successful-py-test-run
    import sys
    if 'threading' in sys.modules:
        del sys.modules['threading']
    import gevent
    import gevent.monkey
    gevent.monkey.patch_all()

    # Setup logger & config
    from tranny.app import config
    # Execute the user command
    arguments = parse_args()

    try:
        if arguments.loglevel:
            log_level = arguments.loglevel.upper()
        elif config.has_option("log", "level"):
            log_level = config.get_default("log", "level")
        else:
            log_level = "INFO"
        log_fmt = config.get_default("log", "format", "%(asctime)s - %(message)s")
        logging.basicConfig(level=logging.getLevelName(log_level), format=log_fmt)

        if arguments.config:
            config.initialize(arguments.config)
        arguments.func(arguments)
    except Exception:
        logging.exception("Fatal error, cannot start!")
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
