# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, Required
from flask.ext.pagedown.fields import PageDownField
from flask_ckeditor import CKEditor, CKEditorField


class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)]) 
    location = StringField('Location', validators=[Length(0, 64)]) 
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    body = CKEditorField("What's on your mind now? (Use Markdown text.)", validators=[Required()])
    submit = SubmitField('Submit')


class GeneralForm(FlaskForm):
    input = StringField('id', validators=[Length(0, 64)])
    submit = SubmitField('Submit')
