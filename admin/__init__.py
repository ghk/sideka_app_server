import sys

sys.path.append('../common')

from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
from common.database import db
from common.marshmallow import ma


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../common/app.cfg')
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['ADMIN_SQLALCHEMY_DATABASE_URI']
    app.config['SQLALCHEMY_BINDS'] = {
        'sideka': app.config['ADMIN_SQLALCHEMY_DATABASE_URI']
    }
    app.secret_key = app.config["SECRET_KEY"]
    CORS(app)
    db.init_app(app)
    ma.init_app(app)
    return app


def create_login_manager(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "users.login"
    return login_manager

