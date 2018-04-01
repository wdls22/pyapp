# -*- coding: utf-8 -*-

from datetime import datetime
from flask import render_template
import os
import time
from os import environ
from sqlite3 import dbapi2 as sqlite3
from flask import current_app, request, session, g, redirect, url_for, abort, \
     render_template, flash
from wtforms import Form, BooleanField, TextField, PasswordField, validators, StringField


time_format = '%Y-%m-%d %X'
app = current_app


@app.route('/login1', methods=['GET', 'POST'])
def login1():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = g.db.execute('select id, name, password, email from users')
        find = 0
        for row in cur.fetchall():
            if row[1] == username:
                find = 1
                id = row[0]
                true_password = row[2]
                break
        if find == 1:
            if password == true_password:
                curr_user = User()
                curr_user.id = id
                next = request.args.get('next')
                return redirect(next or url_for('show_entries'))
        flash('Wrong username or password')
        return render_template('login1.html')
    else:
        return render_template('login1.html')

    #
    #
    # user = User.objects(name=username,
    #                     password=password).first()
    # if user:
    #     login_user(user)
    #     return jsonify(user.to_json())
    # else:
    #     return jsonify({"status": 401,
    #                     "reason": "Username or Password Error"})
    #


def query_user(id):
    cur = g.db.execute('select id from users')
    if len(cur.fetchall()) != 0:
        id = cur.fetchall()[0][0]
    else:
        id = -1
    return id


#
# @login_manager.user_loader
# def load_user(user_id):
#     if query_user(user_id) != -1:
#         curr_user = User()
#         curr_user.id = user_id
#         return curr_user
#


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    # use with get_db
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:

        db.cursor().executescript(f.read())
    db.commit()

#
# @app.cli.command('initdb')
# def initdb_command():
#     """Initializes the database."""
#     init_db()
#     print 'Initialized the database.'


@app.route('/')
@app.route('/home')
def show_entries():
    cur = g.db.execute('select id, title, text, times from entries order by id desc')
    # print cur.fetchall()
    entries = [dict(id=row[0], title=row[1], text=row[2], times=row[3]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)


@app.route('/user_entries')
def show_user_entries():
    cur = g.db.execute('select id, title, text, times from user_entries order by id desc')
    # print cur.fetchall()
    entries = [dict(id=row[0], title=row[1], text=row[2], times=row[3]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    return redirect(url_for('show_entries'))


@app.before_request
def before_request():
    g.db = connect_db()