"""
The flask application package.
"""
import os
import time
from os import environ
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import login_user
from flask_login import logout_user

from wtforms import Form, BooleanField, TextField, PasswordField, validators



app = Flask(__name__)

# import Flasker.views
