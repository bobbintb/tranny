# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from os.path import join
from sqlalchemy import create_engine
from tranny.app import Base

__author__ = "Leigh MacDonald <leigh.macdonald@gmail.com>"
__license__ = "BSD 3-Clause"
__copyright__ = "Copyright (c) 2013-2014 Leigh MacDonald"
__version__ = '0.0.1'

import argparse
import logging


def run_application(options):
    import gevent
    import signal
    from tranny.manager import ServiceManager

    gevent.signal(signal.SIGQUIT, gevent.kill)

    application = ServiceManager()
    from tranny.app import event_manager

    from tranny import metadata

    for handler in metadata.get_handlers():
        event_manager.register_handler(handler)
    application.start()


def parse_args(args=None):
    """ Parse command line argument and launch the appropriate command specifid
    by the user input
    """

    def cmd_start(options):
        run_application(options)

    def cmd_db_drop(options):
        from tranny.datastore import db_drop

        db_drop()

    def cmd_db_init(options):
        from tranny.datastore import db_drop, db_init

        db_init(username=options.username, password=options.password, wipe=options.wipe)

    def cmd_cache_clear(options):
        from tranny import cache

        cache.invalidate()

    def cmd_imdb(options):
        from tranny.service import imdb

        imdb.load_sql(options.nodownload)

    def cmd_geoip(options):
        from tranny.service import geoip
        from tranny.app import Session
        from tranny.app import config

        engine = create_engine(config.get_db_uri())
        Session.configure(bind=engine)
        Base.metadata.create_all(bind=engine)

        db_file_path = geoip.fetch_update(download=options.nodownload)
        geoip.update(Session(), db_file_path)

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

    imdb = subparsers.add_parser(
        "imdb",
        help="Load and manage the imdb SQL database (warn: This can take 1-10 hrs to complete"
    )
    imdb.add_argument("-n", "--nodownload",
                      help="Do not download the datasets before loading (assumes existing data)",
                      action="store_false")
    imdb.set_defaults(func=cmd_imdb)

    geoip = subparsers.add_parser("geoip", help="Load and manage the geoip database")
    geoip.add_argument("-n", "--nodownload",
                       help="Do not download the datasets before loading (assumes existing data)",
                       action="store_false")
    geoip.set_defaults(func=cmd_geoip)

    return parser.parse_args(args=args)


def setup_logging(config, log_level):
    # Disable 3rd party debug messages when in debug mode
    # TODO make TRACE logging level for 3rd party modules to output debug messages
    def gen_conf():
        log_conf = {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'verbose': {
                    'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
                },
                'default': {
                    'format': config.get_default("log", "format", "%(levelname)s %(asctime)s %(name)s: %(message)s")
                },
            },
            'handlers': {
                'console': {
                    'level': log_level,
                    'class': 'logging.StreamHandler',
                    'formatter': 'default'
                },
                'email': {
                    'level': 'ERROR',
                    'class': 'logging.handlers.SMTPHandler',
                    'mailhost': config.get_default("mail", "server", "localhost"),
                    'fromaddr': config.get_default("mail", 'fromaddr', ""),
                    'toaddrs': config.get_default("mail", "toaddr", "").split(","),
                    'subject': "Tranny Application Error",
                    'credentials': [
                        config.get_default("mail", "username", ""),
                        config.get_default("mail", "password")
                    ]
                },
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': log_level,
                    'filename': join(config.config_path, 'polytorrent.log'),
                    'mode': 'a',
                    'maxBytes': 10485760,
                    'backupCount': 5
                }
            },
            'loggers': {
                '': {
                    'level': log_level,
                    'handlers': ['console']
                }
            }
        }

        def set_log_levels(loggers, level):
            for logger_name in loggers:
                log_conf['loggers'][logger_name] = {'level': level}

        set_log_levels(['GuessEpisodeInfoFromPosition', 'GuessProperties',
                        'GuessEpisodesRexps', 'GuessReleaseGroup',
                        'guessit.matcher', 'GuessEpisodeDetails',
                        'GuessEpisodeInfoFromPosition'], logging.ERROR)

        set_log_levels(['requests', 'imdbpy', 'guessit'], logging.WARNING)

        if config.get_default_boolean("log", "email_enabled", False):
            log_conf['loggers']['']['handlers'].append("email")
        if config.get_default_boolean("log", "file_enabled", True):
            log_conf['loggers']['']['handlers'].append("file")
        return log_conf
    import logging.config as lc

    lc.dictConfig(gen_conf())


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

        setup_logging(config, log_level)

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
