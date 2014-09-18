# -*- coding: utf-8 -*-
"""
User handling functions
"""
from __future__ import unicode_literals
from functools import partial
import hashlib
from flask import Blueprint, redirect, url_for, request, flash
from flask.ext.login import logout_user, login_user
from tranny import ui
from tranny.app import Session
from tranny.models import User

section_name = "user"
usr = Blueprint(section_name, __name__, url_prefix="/user")
renderer = partial(ui.render, section=section_name)


@usr.route("/login")
@renderer("login.html")
def login():
    """ Show the user login form """
    pass


@usr.route("/login/perform", methods=['POST'])
def login_perform():
    """ Handle a user login form

    :return: Redirect the user to the previous page or the home index
    :rtype: dict
    """
    try:
        user_name = request.values['user_name']
        user_password = request.values['user_password']
    except KeyError:
        pass
    else:
        session = Session()
        user = session.query(User).filter_by(user_name=user_name).first()
        if not user or not user.password == hashlib.sha1(user_password).hexdigest():
            flash("Invalid credentials", "alert")
            return redirect(url_for(".login"))
        try:
            remember = request.values['remember'].lower() == "on"
        except KeyError:
            remember = False
        login_user(user, remember=remember)
    return redirect(request.args.get("next") or url_for("home.index"))


@usr.route("/logout")
def logout():
    """ Make the user logout of their current session

    :return: Redirect to the login page
    :rtype: Response
    """
    logout_user()
    return redirect(url_for(".login"))
