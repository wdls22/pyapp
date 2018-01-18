import os
import time
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request
from . import main
from ..models import Entries, db, User
from flask_login import login_required, current_user


@main.route('/')
@main.route('/home')
def show_entries():
    entry = db.session.query(Entries.id, Entries.title, Entries.text, Entries.times, User.username).\
        filter(Entries.author_id == User.id).order_by(Entries.times.desc()).all()
    entries = [dict(id=row.id, title=row.title, text=row.text, times=row.times, author=row.username) for row in entry]
    return render_template('show_entries.html', entries=entries)


@main.route('/delete', methods=['POST'])
@login_required
def delete_entry():
    id = request.form['entry_id']
    user_entry = Entries.query.filter_by(id=id).first()
    if int(user_entry.author_id) != int(current_user.get_id()):
        flash('You can not delete entry not belongs to you')
        return redirect(url_for('main.show_entries'))
    Entries.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('main.show_entries'))


@main.route('/add', methods=['POST'])
@login_required
def add_entry():
    if request.form['title'] == "" or request.form['text'] == "":
        flash('empty is illegal')
        return redirect(url_for('main.show_entries'))
    new_entry = Entries(title=request.form['title'],
                        text=request.form['text'],
                        times=datetime.now(),
                        author_id=current_user.get_id())
    db.session.add(new_entry)
    db.session.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('main.show_entries'))

