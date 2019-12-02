from flask import render_template, request, Blueprint, flash
from sqlalchemy_paginator import Paginator
from flaskbase.database import session

main = Blueprint('main',__name__)

@main.route("/")
def index():
    return render_template('index.html', title="Title")
