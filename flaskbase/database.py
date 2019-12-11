from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import Config

Base = declarative_base()

engine = create_engine(Config.DATABASE_URI)
Base.metadata.bind = engine
DBSession = sessionmaker(autocommit=False,autoflush=False,bind=engine)
session = DBSession()

def init_db():
    from flaskbase.models import User
    Base.metadata.create_all(bind=engine)