# -*- coding: utf-8 -*-

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

    parser = argparse.ArgumentParser(prog="tranny-cli.py", description="Tranny torrent management system")
    subparsers = parser.add_subparsers(help="Command help")

    db_init = subparsers.add_parser("db_init")
    db_init.add_argument("-u", "--username", help="Admin username", default="admin")
    db_init.add_argument("-p", "--password", help="Admin password", default="tranny")
    db_init.add_argument("-w", "--wipe", help="Wipe any existing database", action="store_true")
    db_init.set_defaults(func=cmd_db_init)

    db_drop = subparsers.add_parser("drop_db", help="Drop (delete) the existing database. This is non-reversible.")
    db_drop.set_defaults(func=cmd_db_drop)

    sp_run = subparsers.add_parser("run")
    sp_run.set_defaults(func=cmd_start)

    return parser.parse_args()


def main():
    logging.basicConfig(level=logging.INFO)
    from tranny.app import config
    arguments = parse_args()
    arguments.func(arguments)


if __name__ == '__main__':
    main()
