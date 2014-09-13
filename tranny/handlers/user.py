# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from flask import Blueprint, redirect, url_for, request, flash
from flask.ext.login import logout_user, login_user
from tranny import models, ui
import hashlib

usr = Blueprint("user", __name__, url_prefix="/user")


@usr.route("/login")
def login():
    return ui.render_template("login.html")


@usr.route("/login/perform", methods=['POST'])
def login_perform():
    try:
        user_name = request.values['user_name']
        user_password = request.values['user_password']
    except KeyError:
        pass
    else:
        user = models.User.query.filter_by(user_name=user_name).first()
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
    logout_user()
    return redirect(url_for(".login"))
