# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from flask import render_template as flask_render_template


def render_template(template_name, track_next=True, **kwargs):
    return flask_render_template(template_name, **kwargs)
