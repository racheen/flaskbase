import os
from flask import render_template, request, url_for, flash, redirect, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy_paginator import Paginator
from flask import current_app
from flaskbase import bcrypt, mail
from flaskbase.models import User
from flaskbase.database import session
from flaskbase.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from flaskbase.users.utils import pagination, save_picture, send_reset_email, send_confirm_email

users = Blueprint('users',__name__)

@users.route("/register", methods=['POST','GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,email=form.email.data, password=hashed_password)
        session.add(user)
        session.commit()
        flash('Account created for {}!'.format(form.username.data), 'success')
        # send_confirm_email(user)
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

@users.route("/login", methods=['POST','GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('users.login'))
    form = LoginForm()
    if form.validate_on_submit():
        user =  session.query(User).filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('You have been logged in!', 'success')
            return render_template('welcome.html', title='Welcome', user=user)
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('users.login'))

@users.route("/account", methods=['POST','GET'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_path = os.path.join(current_app.root_path, 'static/profile_pics', current_user.image_file)
            if current_user.image_file != 'default.jpg':
                os.remove(picture_path) 
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        if current_user.email != form.email.data:
            current_user.confirmed_email = False
        current_user.username = form.username.data
        current_user.email = form.email.data
        session.commit()
        flash('Your account has been updated','success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form, confirm_email=current_user.confirmed_email)

@users.route("/resend_confirm_email")
@login_required
def resend_confirm_email():
    send_confirm_email(current_user)
    flash('An email has been sent. Check your inbox.','success')
    return redirect(url_for('users.account'))

@users.route("/confirm_email/<token>", methods=['GET','POST'])
def confirm_email(token):
    user = User.verify_confirm_email(token)
    if user is None:
        flash('That is an invalid or expired token','warning')
        return redirect(url_for('main.home'))
    user.confirmed_email = True
    session.commit()
    flash('Email has been confirmed.','success')
    return redirect(url_for('main.home'))

@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page',1,type=int)
    user = session.query(User).filter_by(username=username).first()
    if not user:
        return render_template("errors/404.html")
    query = session.query(Post).filter_by(author=user).order_by(Post.date_posted.desc())
    posts = Paginator(query, 5)
    if page > posts.pages_range[-1]:
        return render_template("errors/404.html")
    posts_page = posts.page(page)
    show_pages = pagination(page, posts.pages_range)
    return render_template('user_posts.html', query=query, posts_page=posts_page, posts=posts, show_pages=show_pages, user=user)

@users.route("/reset_password", methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = session.query(User).filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset the password','info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title="Reset Password", form=form)

@users.route("/reset_password/<token>", methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token','warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        session.commit()
        flash('Your password has been updated! You are now able to login.', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title="Reset Password", form=form)

