from multiprocessing import Process
from logging import getLogger, INFO
from json import dumps
from ConfigParser import NoSectionError, NoOptionError
from flask import Flask, url_for, redirect, session, render_template, g
from flask.ext.login import LoginManager, confirm_login
from tranny.info import file_size
from tranny import datastore

log = getLogger("tranny.web")

app_thread = None

# Setup Flask environment
app = Flask("tranny")
app.debug_log_format = "%(asctime)s - %(message)s"
app.logger.setLevel(INFO)
app.jinja_env.filters['file_size'] = file_size

# Setup Flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "webui.login"
login_manager.session_protection = "strong"


@login_manager.user_loader
def user_loader(user_id):
    return datastore.fetch_user(user_id=user_id)


@login_manager.needs_refresh_handler
def refresh():
    # do stuff
    confirm_login()
    return True


def render(template_name, **kwargs):
    try:
        kwargs['messages'] = session['messages']
        del session['messages']
    except KeyError:
        pass
    return render_template(template_name, **kwargs)


def response(status=0, msg=None):
    return dumps({
        'status': status,
        'msg': msg
    })


@app.before_request
def before_request():
    from tranny import session
    g.session = session


@app.route("/")
def index():
    return redirect(url_for("webui.index"))


def add_user_message(message, class_name=""):
    try:
        session['messages'].append()
    except KeyError:
        session['messages'] = [[message, class_name]]


def start(listen_host="localhost", listen_port=8080, debug=True):
    global app_thread
    if not app_thread:
        from webui import webui
        from tranny import config
        try:
            secret_key = config.get("general", "secret_key")
            if not secret_key:
                raise NoOptionError("general", "secret_key")
        except (NoSectionError, NoOptionError):
            raise Exception("Failed to find secret_key, please set it before enabling the webui")
        else:
            app.secret_key = secret_key
        app.register_blueprint(webui)
        args = {
            'debug': debug,
            'host': listen_host,
            'port': int(listen_port),
            'use_debugger': True,
            'use_reloader': False  # Breaks debugging via pycharm
        }
        app_thread = Process(target=app.run, kwargs=args)
    if app_thread and not app_thread.is_alive():
        log.info("Starting web ui handler")
        app_thread.start()


def stop():
    global app_thread
    if app_thread.is_alive():
        log.info("Waiting for web handler thread to terminate")
        app_thread.terminate()
        app_thread.join()
