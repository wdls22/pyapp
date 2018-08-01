# -*- coding: utf-8 -*-
import os
import time
import urllib
import hashlib
from time import time
import xml.etree.ElementTree as ET
from ..utinity import utinity, zhihu
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, abort, current_app, make_response
from . import main
from ..models import Entries, db, User, Post
from .forms import EditProfileForm, PostForm, GeneralForm
from flask_login import login_required, current_user
from flask_moment import Moment


@main.route('/')
@main.route('/home')
def show_entries():
    entry = db.session.query(Entries.id, Entries.title, Entries.text, Entries.times, User.username, Entries.author_id).\
        filter(Entries.author_id == User.id).order_by(Entries.times.desc()).all()
    entries = [dict(id=row.id, title=row.title, text=row.text, times=row.times, author=row.username, author_id=row.author_id) for row in entry]
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
                        times=datetime.utcnow(),
                        author_id=current_user.get_id())
    db.session.add(new_entry)
    db.session.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('main.show_entries'))


@main.route('/user/<username>', methods=['GET', 'POST'])
def user(username):
    username = utinity.convert_url_uni(username)
    form = PostForm()
    user = User.query.filter_by(username=username).first()
    if user is None:
        return abort(404)
    if hasattr(current_user, 'username') and current_user.username == username and \
            form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('main.user', username=username))
    # posts = user.posts.order_by(Post.timestamp.desc()).all()

    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, form=form, posts=posts, pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST']) 
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/post/<username>', methods=['GET', 'POST'])
def post(username):
    username = utinity.convert_url_uni(username)
    form = PostForm()
    if current_user.username == username and \
            form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('post.html', form=form, posts=posts)


@main.route('/<username>/delete', methods=['POST'])
@login_required
def delete_post(username):
    username = utinity.convert_url_uni(username)
    id = request.form['post_id']
    post = Post.query.filter_by(id=id).first()
    if int(post.author_id) != int(current_user.get_id()):
        flash('You can not delete entry not belongs to you')
        return redirect(url_for('main.user', username=username))
    Post.query.filter_by(id=id).delete()
    db.session.commit()
    flash('Your post has been deleted successfully.')
    return redirect(url_for('main.user', username=current_user.username))


@main.route('/follow/<username>')
@login_required
def follow(username):
    username = utinity.convert_url_uni(username)
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.show_entries'))
    if current_user.is_following(user):
        flash('You have already followed this user.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('You are now following %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
def unfollow(username):
    username = utinity.convert_url_uni(username)
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.show_entries'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    username = utinity.convert_url_uni(username)
    user = User.query.filter_by(username=username).first() 
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.show_entries'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
                for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                        endpoint='.followers', pagination=pagination,
                        follows=follows)


@main.route('/followed_by/<username>')
def followed_by(username):
    username = utinity.convert_url_uni(username)
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/all_users')
def all_users():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    users = pagination.items

    return render_template('all_users.html', users=users, title='All users',
                           endpoint='.all_users', pagination=pagination)


@main.route('/zhihu_id', methods=['GET', 'POST'])
def zhihu_id():
    form = GeneralForm()
    qid = form.input.data
    if form.validate_on_submit():
        qid = form.input.data
        url_list = zhihu.get_image_url(qid)
        if url_list is not None:
            return render_template('zhihu.html', endpoint='.zhihu_id', url_list=url_list, qid=qid)
        return redirect(url_for('main.zhihu_id'))
    return render_template('zhihu_id.html', form=form)

    

@main.route('/wechat',methods=['GET','POST'])
def wechat():
    if request.method == 'GET':
        #这里改写你在微信公众平台里输入的token
        token = 'shengtokentoken'
        #获取输入参数
        data = request.args
        signature = data.get('signature','')
        timestamp = data.get('timestamp','')
        nonce = data.get('nonce','')
        echostr = data.get('echostr','')
        #字典排序
        list = [token, timestamp, nonce]
        list.sort()

        s = list[0] + list[1] + list[2]
        #sha1加密算法        
        hascode = hashlib.sha1(s.encode('utf-8')).hexdigest()
        #如果是来自微信的请求，则回复echostr
        if hascode == signature:
            return echostr
        else:
            return ""

    if request.method == "POST":
        rec=request.stream.read()
        xml_rec = ET.fromstring(rec)
        ToUserName = xml_rec.find('ToUserName').text
        fromUser = xml_rec.find('FromUserName').text
        MsgType = xml_rec.find('MsgType').text
        Content = xml_rec.find('Content').text
        MsgId = xml_rec.find('MsgId').text

        reply = """<xml>
                  <ToUserName> <![CDATA[%s]]></ToUserName>
                  <FromUserName><![CDATA[%s]]></FromUserName>
                  <CreateTime>%s</CreateTime>
                  <MsgType><![CDATA[text]]></MsgType>
                  <Content><![CDATA[%s]]></Content>
                  </xml>"""

        response = make_response(reply % (fromUser, ToUserName, str(int(time())), Content))
        response.content_type = 'application/xml'
        return response 
