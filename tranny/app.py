# -*- coding: utf-8 -*-
"""
Main application entry point. Defines several global vars which are used throughout the
application.
"""
from __future__ import unicode_literals, absolute_import
import httplib
import os
from json import dumps
from flask import Flask, g, redirect, url_for, session, _app_ctx_stack
from flask.ext.login import current_user, confirm_login
from flask.ext.uploads import configure_uploads, patch_request_class
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session


# Setup global configuration
from tranny import configuration
config = configuration.Configuration()
config.initialize()

# Init cache
from tranny import cache
cache.configure(config)

# Init db
engine = create_engine(config.get_db_uri())
# Setup sqlalchemy session factory
Base = declarative_base()
session_factory = sessionmaker()
# scopefunc determines our current context, we use flasks context for this to allow usage from the
# flask views and outside of flask interchangeably
Session = scoped_session(session_factory, scopefunc=_app_ctx_stack.__ident_func__)

torrent_client = None

from tranny.models import User
from tranny.util import file_size
from tranny import ui
from tranny.extensions import mail, login_manager, socketio

__all__ = ['create_app', 'config', 'Session']


def create_app(app_name="tranny"):
    """ Configure a flask application instance ready to launch

    :param app_name: Name of the application
    :type app_name: unicode
    :return: Configured flask instance
    :rtype: Flask
    """

    app = Flask(app_name)
    configure_app(app)
    configure_extensions(app)
    configure_hook(app)
    configure_blueprints(app)
    configure_logging(app)
    configure_template_filters(app)
    configure_error_handlers(app)
    return app


def configure_app(app):
    """ Load the flask application configuration file from disk and configure the flask
    relevant section.

    :param app: Application instance
    :type app: Flask
    """
    config.init_app(app)

    @app.route("/")
    def index():
        return redirect(url_for("home.index"))

    from tranny import forms

    @app.context_processor
    def inject_global_tpl_vars():
        kwargs = dict()
        try:
            kwargs['messages'] = session['messages']
            del session['messages']
        except KeyError:
            pass
        # Upload form is included in all pages so its injected globally.
        kwargs['upload_form'] = forms.UploadForm.make()
        return kwargs


def configure_extensions(app):
    """ Load and configure 3rd party flask extensions

    :param app: Application instance
    :type app: Flask
    """

    # flask-mail
    mail.init_app(app)

    # flask-socketio
    socketio.init_app(app)

    # flask-uploads
    from tranny.forms import torrent_file_set
    configure_uploads(app, [torrent_file_set])
    patch_request_class(app)

    # flask-babel
    #babel = Babel(app)

    #@babel.localeselector
    #def get_locale():
    #    accept_languages = app.config.get('ACCEPT_LANGUAGES')
    #    return request.accept_languages.best_match(accept_languages)

    # flask-login
    login_manager.login_view = 'user.login'
    login_manager.refresh_view = 'frontend.reauth'

    @login_manager.user_loader
    def user_loader(user_id):
        return Session().query(User).filter_by(user_id=user_id).first()

    @login_manager.needs_refresh_handler
    def refresh():
        # do stuff
        confirm_login()
        return True

    @login_manager.unauthorized_handler
    def login_redir():
        return redirect(url_for("user.login"))

    @login_manager.user_loader
    def load_user(user_id):
        return Session().query(User).get(user_id)

    login_manager.init_app(app)


def configure_hook(app):
    """ Setup always available pre request context values

    :param app: Application instance
    :type app: Flask
    """
    @app.before_request
    def before_request():
        g.user = current_user


def configure_blueprints(app):
    """ Import and initialize all flask blueprint route handlers

    :param app: Application instance
    :type app: Flask
    """
    from tranny.handlers.filters import filters
    from tranny.handlers.home import home
    from tranny.handlers.rss import rss
    from tranny.handlers.services import services
    from tranny.handlers.settings import settings
    from tranny.handlers.stats import stats
    from tranny.handlers.user import usr
    from tranny.handlers.upload import upload
    from tranny.handlers.torrents import torrents
    map(app.register_blueprint, [filters, home, rss, services, settings, stats, usr, upload, torrents])


def configure_template_filters(app):
    """ Configure extra global jinja2 filters

    :param app: Application instance
    :type app: Flask
    """
    @app.template_filter()
    def pretty_date(value):
        return pretty_date(value)

    @app.template_filter()
    def format_date(value, format='%Y-%m-%d'):
        return value.strftime(format)

    @app.template_filter()
    def human_size(value):
        return file_size(value)


def configure_logging(app):
    """Configure file(info) and email(error) logging."""

    if app.debug or app.testing:
        # Skip debug and test mode. Just check standard output.
        return

    import logging
    from logging.handlers import SMTPHandler

    # Set info level on logger, which might be overwritten by handers.
    # Suppress DEBUG messages.
    app.logger.setLevel(logging.INFO)

    info_log = os.path.join(app.config['LOG_FOLDER'], 'info.log')
    info_file_handler = logging.handlers.RotatingFileHandler(info_log, maxBytes=100000, backupCount=10)
    info_file_handler.setLevel(logging.INFO)
    info_file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    )
    app.logger.addHandler(info_file_handler)

    # Testing
    #app.logger.info("testing info.")
    #app.logger.warn("testing warn.")
    #app.logger.error("testing error.")
    
    if config.has_option("general", "email"):
        mail_handler = SMTPHandler(app.config['MAIL_SERVER'],
                                   app.config['MAIL_USERNAME'],
                                   config.get("general", "email"),
                                   'O_ops... Tranny failed!',
                                   (app.config['MAIL_USERNAME'],
                                    app.config['MAIL_PASSWORD']))
        mail_handler.setLevel(logging.ERROR)
        mail_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]')
        )
        app.logger.addHandler(mail_handler)


def configure_error_handlers(app):

    @app.errorhandler(403)
    def forbidden_page(error):
        return ui.render_template("errors/forbidden_page.html", error=error), httplib.FORBIDDEN

    @app.errorhandler(404)
    def page_not_found(error):
        return ui.render_template("errors/page_not_found.html", error=error), httplib.NOT_FOUND

    @app.errorhandler(500)
    def server_error_page(error):
        return ui.render_template("errors/server_error.html", error=error), httplib.INTERNAL_SERVER_ERROR


def response(status=0, msg=None):
    return dumps({
        'status': status,
        'msg': msg
    })
