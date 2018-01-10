from datetime import datetime
from flask import render_template
from wdls import app
import os
import time
from os import environ
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
# from wtforms import Form, BooleanField, TextField, PasswordField, validators



ISOTIMEFORMAT = '%Y-%m-%d %X'

class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=3, max=25)])
    email = TextField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.Required()])


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        g.db.execute('insert into users (name, password, email) values (?, ?, ?)',
                     [request.form['username'], request.form['password'], request.form['email']])
        g.db.commit()

        flash('Thanks for registering')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


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


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    if request.form['title'] == "" or request.form['text'] == "":
        flash('empty is illegal')
        return redirect(url_for('show_entries'))
    g.db.execute('insert into entries (title, text, times) values (?, ?, ?)',
                 [request.form['title'], request.form['text'], time.strftime(ISOTIMEFORMAT, time.localtime())])
    g.db.commit()
    print time.strftime(ISOTIMEFORMAT, time.localtime())
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/delete', methods=['POST'])
def delete_entry():
    if not session.get('logged_in'):
        flash('please login first')
        return redirect(url_for('login'))
    g.db.execute('DELETE FROM entries WHERE id = ?',
                 [request.form['entry_id']])
    g.db.commit()
    return redirect(url_for('show_entries'))


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


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


@app.before_request
def before_request():
    g.db = connect_db()
