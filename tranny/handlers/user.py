from flask import Blueprint, redirect, url_for, request
from flask.ext.login import logout_user, login_user
from ..models import User
from ..ui import render_template

usr = Blueprint("user", __name__, url_prefix="/user")


@usr.route("/login")
def login():
    return render_template("login.html")


@usr.route("/login/perform", methods=['POST'])
def login_perform():
    try:
        user_name = request.values['user_name']
        user_password = request.values['user_password']
    except KeyError:
        pass
    else:
        user = User.query.filter_by(user_name=user_name).first()
        if not user:
            pass
        if not user.password == user_password:
            pass

        try:
            remember = request.values['remember'].lower() == "on"
        except KeyError:
            remember = False
        login_user(user, remember=remember)
    return redirect(request.args.get("next") or url_for(".index"))


@usr.route("/logout")
def logout():
    logout_user()
    return redirect(url_for(".login"))
