# -*- encoding: utf-8 -*-

from flask import render_template
from foodtruck import app


@app.route('/')
def main_webview():
    return render_template('index.html')
