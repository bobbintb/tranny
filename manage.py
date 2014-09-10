#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Application managements script
"""
from __future__ import unicode_literals
import signal
import sys
from flask.ext.script import Manager
import gevent
from tranny import create_app, app
from tranny.app import Session, Base, engine
from tranny.extensions import socketio
from tranny.models import User
from tranny.constants import ROLE_ADMIN

try:
    import __builtin__
    input = getattr(__builtin__, 'raw_input')
except (ImportError, AttributeError):
    pass

application = create_app()


def shutdown_app(signal, frame):
    print("\b\bClosing tranny..")
    if application.services.client.connected:
        del application.services.client
    sys.exit(0)


signal.signal(signal.SIGINT, shutdown_app)
signal.signal(signal.SIGTERM, shutdown_app)
manager = Manager(application)


@manager.command
def run():
    """Run in local machine."""
    gevent.signal(signal.SIGQUIT, gevent.kill)
    from tranny.manager import ServiceManager
    a = ServiceManager()
    #host = app.config.get_default('flask', 'listen_host', 'localhost')
    #port = app.config.get_default('flask', 'listen_port', 5000, int)
    #socketio.run(application, host=host, port=port)


@manager.command
def dropdb():
    for tbl in reversed(Base.metadata.sorted_tables):
        print("Dropping: {}".format(tbl.name))
        tbl.drop(engine)


@manager.command
def initdb(ask=False):
    """Init/reset database."""
    dropdb()
    Session.configure(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = Session()
    if ask:
        user_name = input("Admin user name [admin]: ")
        if not user_name:
            user_name = "admin"
        password = None
        while not password:
            pw_1 = input("Password: ")
            pw_2 = input("Password Verify: ")
            if pw_1 and pw_1 == pw_2:
                password = pw_1
    else:
        user_name = "admin"
        password = "admin"
    admin = User(user_name=user_name, password=password, role=ROLE_ADMIN)
    session.add(admin)
    session.commit()


manager.add_option('-c', '--config', dest="config", required=False, help="config file")

if __name__ == "__main__":
    manager.run()
