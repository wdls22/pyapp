# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, Required


class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)]) 
    location = StringField('Location', validators=[Length(0, 64)]) 
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    body = TextAreaField("What's on your mind now?", validators=[Required()])
    submit = SubmitField('Submit')


class GeneralForm(FlaskForm):
    input = StringField('id', validators=[Length(0, 64)])
    submit = SubmitField('Submit')
