import httplib
from json import dumps
import os
from flask import Flask, g, request, redirect, url_for
from flask.ext.babel import Babel
from flask.ext.login import current_user, confirm_login
from .models import User
from .configuration import Configuration
from .util import file_size
from .ui import render_template
from .extensions import db, mail, cache, login_manager


__all__ = ['create_app']

config = Configuration()


def create_app(app_name="tranny"):
    app = Flask(app_name)
    configure_app(app)
    configure_hook(app)
    configure_blueprints(app)
    configure_extensions(app)
    configure_logging(app)
    configure_template_filters(app)
    configure_error_handlers(app)
    return app


def configure_app(app):
    config.init_app(app)


def configure_extensions(app):
    # flask-sqlalchemy
    db.init_app(app)

    # flask-mail
    mail.init_app(app)

    # flask-cache
    cache.init_app(app)

    # flask-babel
    babel = Babel(app)

    @babel.localeselector
    def get_locale():
        accept_languages = app.config.get('ACCEPT_LANGUAGES')
        return request.accept_languages.best_match(accept_languages)

    # flask-login
    login_manager.login_view = 'frontend.login'
    login_manager.refresh_view = 'frontend.reauth'

    @login_manager.user_loader
    def user_loader(user_id):
        return User.query.filter_by(user_id=user_id).first()

    @login_manager.needs_refresh_handler
    def refresh():
        # do stuff
        confirm_login()
        return True

    @login_manager.unauthorized_handler
    def login_redir():
        return redirect(url_for(".login"))

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    login_manager.init_app(app)


def configure_hook(app):
    @app.before_request
    def before_request():
        from tranny import session

        g.session = session
        g.user = current_user


def configure_blueprints(app):
    from .handlers.filters import filters
    from .handlers.home import home
    from .handlers.rss import rss
    from .handlers.services import services
    from .handlers.settings import settings
    from .handlers.stats import stats
    from .handlers.user import usr
    map(app.register_blueprint, [filters, home, rss, services, settings, stats, usr])


def configure_template_filters(app):

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

    mail_handler = SMTPHandler(app.config['MAIL_SERVER'],
                               app.config['MAIL_USERNAME'],
                               app.config['ADMINS'],
                               'O_ops... %s failed!' % app.config['PROJECT'],
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
        return render_template("errors/forbidden_page.html"), httplib.FORBIDDEN

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/page_not_found.html"), httplib.NOT_FOUND

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("errors/server_error.html"), httplib.INTERNAL_SERVER_ERROR


def response(status=0, msg=None):
    return dumps({
        'status': status,
        'msg': msg
    })
