# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from flask import session, render_template as flask_render_template


def render_template(template_name, **kwargs):
    try:
        kwargs['messages'] = session['messages']
        del session['messages']
    except KeyError:
        pass
    return flask_render_template(template_name, **kwargs)
