# -*- coding: utf-8 -*-

import os
import time
from os import environ
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
from auth import login_manager
from models import db, User
from flask_moment import Moment
# from flask_login import UserMixin
# from flask_login import login_user
# from flask_login import logout_user
# from wtforms import Form, BooleanField, TextField, PasswordField, validators

from .main import main as main_blueprint
from .auth import auth as auth_blueprint


# create our little application :)

bootstrap = Bootstrap()
moment = Moment()

def create_app(config_name):
    app = Flask(__name__)
    print config
    app.config.from_object(config[config_name])
    login_manager.init_app(app)
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
        db.session.commit()

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.config.from_envvar('FLASKR_SETTINGS', silent=True)

    return app

