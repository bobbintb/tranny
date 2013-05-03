from multiprocessing import Process
from logging import getLogger
from flask import Flask, url_for, redirect


log = getLogger("tranny.web")

app_thread = None
app = Flask("tranny")

app.debug_log_format = "%(asctime)s - %(message)s"


@app.route("/")
def index():
    return redirect(url_for("webui.index"))


def start(listen_host="localhost", listen_port=8080, debug=True):
    global app_thread
    if not app_thread:
        from webui import webui

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

