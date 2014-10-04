# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from flask import render_template as flask_render_template, request, jsonify, Response
from six import wraps
from werkzeug.wrappers import Response as WerkzeugResponse


def render_template(template_name, track_next=True, **kwargs):
    return flask_render_template(template_name, **kwargs)


def render(tpl=None, section="home", fmt="html"):
    """ Render output to the clients browser. This function will handle both HTML and JSON
    output by setting the fmt flag to the desired format

    :param tpl: Template to use for HTML output
    :type tpl: string
    :param section: Section name of the template
    :type section: string
    :param fmt: Format of output (html or json)
    :type fmt: string
    :return: Rendered route output
    :rtype: string
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            template_name = tpl
            if template_name is None:
                template_name = request.endpoint.replace('.', '/') + '.html'
            ctx = f(*args, **kwargs)
            if ctx is None:
                ctx = {}
            elif isinstance(ctx, WerkzeugResponse):
                return ctx
            if fmt == "json":
                #return Response(json.dumps(ctx), mimetype='application/json')
                return jsonify(ctx)
            else:
                return flask_render_template(template_name, section=section, **ctx)

        return decorated_function
    return decorator
