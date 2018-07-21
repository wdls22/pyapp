# -*- coding: utf-8 -*-
from flask import render_template, request, jsonify
from . import main

# error handle blue print.
@main.app_errorhandler(404)
def page_not_found(e):
    # if endpoint is not browser, return jason, not HTML.
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def inner_error(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'inner error'})
        response.status_code = 500
        return response
    return render_template('500.html'), 500
