import os

class Config:
    SECRET_KEY = os.environ['SECRET_KEY']
    DATABASE_URI= "sqlite:///test.db"
    TEMPLATES_AUTO_RELOAD = True
    MAIL_SERVER = os.environ['MAIL_SERVER']
    MAIL_PORT = os.environ['MAIL_PORT']
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ['MAIL_USERNAME']
    MAIL_PASSWORD = os.environ['MAIL_PASSWORD']