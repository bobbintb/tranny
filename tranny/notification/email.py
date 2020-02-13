# -*- coding: utf-8 -*-

from contextlib import contextmanager
import smtplib
from email.mime.text import MIMEText
from tranny.app import config
from tranny import plugin
from tranny.events import EventHandler, EVENT_NOTIFICATION

_config_key = 'notification_email'


def send_event(event, payload=None):
    if payload is None:
        payload = dict()


def send_message(body_plain, subject, addr_from, addr_to):
    msg = MIMEText(body_plain)
    msg['Subject'] = subject
    msg['From'] = addr_from
    msg['To'] = addr_to

    with smtp_client() as smtp:
        smtp.sendmail(addr_from, [addr_to], msg.as_string())
    return msg


@contextmanager
def smtp_client():
    """ Create a configured SMTP instance ready to send

    :return:
    :rtype:
    """
    srv = None
    try:
        use_ssl = config.get_default_boolean(_config_key, 'ssl', False)
        username = config.get_default(_config_key, 'username', "")
        password = config.get_default(_config_key, 'password', "")
        args = {
            'host': config.get_default(_config_key, 'host', 'localhost'),
            'port': config.get_default(_config_key, 'port', 25, int)
        }
        if use_ssl:
            srv = smtplib.SMTP_SSL(**args)
        else:
            srv = smtplib.SMTP(**args)
        if config.get_default_boolean(_config_key, 'starttls', False):
            srv.starttls()
        if username and password:
            srv.login(username, password)
        yield srv
    finally:
        if srv and hasattr(srv, 'quit'):
            srv.quit()


class NotificationEmail(plugin.BasePlugin):
    def get_handlers(self):
        return [
            EventHandler(EVENT_NOTIFICATION, self.handle_event_notification)
        ]

    def handle_event_notification(self, payload):
        pass
