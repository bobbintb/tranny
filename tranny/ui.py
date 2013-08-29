# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from flask import session, render_template as flask_render_template
from .forms import UploadForm


def render_template(template_name, track_next=True, **kwargs):

    try:
        kwargs['messages'] = session['messages']
        del session['messages']
    except KeyError:
        pass

    kwargs['upload_form'] = UploadForm.make()

    return flask_render_template(template_name, **kwargs)
