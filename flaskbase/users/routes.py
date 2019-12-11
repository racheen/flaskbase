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
        return redirect(url_for('main.index'))
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

@users.route("/resend_confirm_email")
@login_required
def resend_confirm_email():
    send_confirm_email(current_user)
    flash('An email has been sent. Check your inbox.','success')
    return redirect(url_for('users.account'))

@users.route("/reset_password", methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
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

