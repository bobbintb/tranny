# -*- coding: utf-8 -*-


from flask.ext.mail import Mail
mail = Mail()

from flask.ext.login import LoginManager
login_manager = LoginManager()

from flask.ext.socketio import SocketIO
socketio = SocketIO()
