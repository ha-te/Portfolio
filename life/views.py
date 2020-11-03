import csv
from datetime import date
from datetime import datetime
import locale
import os
from os import chdir
import pathlib
import random
import openpyxl
import json
import requests


from flask import (
    Blueprint, 
    abort, 
    request, 
    render_template,
    redirect, 
    url_for, 
    flash, 
    session, 
    jsonify
)


from life import db


bp = Blueprint('app', __name__, url_prefix='')


@bp.route('/')
def home():
    # session['url'] = 'app.home'
    return render_template('home.html')

# for errorhandling
@bp.app_errorhandler(404)
def page_not_found(e):
    return redirect(url_for('app.home'))

@bp.app_errorhandler(500)
def server_error(e):
    return render_template('500.html')