# flask configuration
import os
import pathlib

from flask_sqlalchemy import SQLAlchemy

class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "rubbish99"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(
        pathlib.Path().absolute(), 'shop.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADS_FOLDER = os.path.join(pathlib.Path().absolute(), 'static\\uploads')
