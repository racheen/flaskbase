from flask import render_template, request, Blueprint, flash, url_for, redirect
from sqlalchemy_paginator import Paginator
from flaskbase.database import session

main = Blueprint('main',__name__)

@main.route("/")
def index():
    return redirect(url_for('users.login'))
