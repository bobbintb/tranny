# -*- coding: utf-8 -*-
from flask.ext.script import Manager

from tranny import create_app
from tranny.extensions import db
from tranny.models import User
from tranny.constants import ROLE_ADMIN


app = create_app()

manager = Manager(app)


@manager.command
def run():
    """Run in local machine."""

    app.run()


@manager.command
def initdb():
    """Init/reset database."""

    db.drop_all()
    db.create_all()

    user_name = raw_input("Admin user name [admin]: ")
    if not user_name:
        user_name = "admin"
    password = None
    while not password:
        pw_1 = raw_input("Password: ")
        pw_2 = raw_input("Password Verify: ")
        if pw_1 and pw_1 == pw_2:
            password = pw_1

    admin = User(user_name=user_name, password=password, role=ROLE_ADMIN)
    db.session.add(admin)
    db.session.commit()


manager.add_option('-c', '--config',
                   dest="config",
                   required=False,
                   help="config file")

if __name__ == "__main__":
    manager.run()
