import secrets
import os
from flask import url_for, current_app
from flaskbase import mail
from PIL import Image
from flask_mail import Message

def pagination(page, pages_range):
    show_pages = []
    if len(pages_range)<5:
        return pages_range
    if page + 2 >= pages_range[-1]:
        n = pages_range[-1] - 4
        while n!=pages_range[-1]+1:
            show_pages.append(n)
            n+=1
    elif page - 2 <= 1:
        n = 1
        while n!=6:
            show_pages.append(n)
            n+=1
    else:
        n = page - 2
        while n!=page+3:
            show_pages.append(n)
            n+=1
    return show_pages

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = form_picture.filename
    if form_picture.filename != 'default.jpg':
        picture_fn = random_hex + f_ext
        picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
        output_size = (125,125)
        i = Image.open(form_picture)
        i.thumbnail(output_size)
        i.save(picture_path)
    return picture_fn

def send_confirm_email(user):
    token = user.get_confirm_token()
    msg = Message(subject='Confirm Email', sender='noreply@demo.com', recipients=[user.email])
    msg.body = ''' To confirm your email, visit the following link:
{}

This link will expire in an hour.
                '''.format(url_for('users.confirm_email',token=token, _external=True))
    mail.send(msg)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(subject='Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    msg.body = ''' To reset your password, visit the following link:
{}

If you did not make this request then simple ignore this email and no changes will be made. This link will expire in 10 mins.
                '''.format(url_for('users.reset_token',token=token, _external=True))
    mail.send(msg)