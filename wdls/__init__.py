import os
import time
from os import environ
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
# from flask_login import LoginManager
# from flask_login import UserMixin
# from flask_login import login_user
# from flask_login import logout_user
from wtforms import Form, BooleanField, TextField, PasswordField, validators



# create our little application :)

app = Flask(__name__)

app.config.from_object(__name__)

# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login1'
# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=False,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',))


app.config.from_envvar('FLASKR_SETTINGS', silent=True)
import wdls.views