import sys

sys.path.append('../common')

from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config.from_object('common.Config')
# app.config.from_object('common.ProductionConfig')
app.config.from_object('common.DevelopmentConfig')
app.config['SQLALCHEMY_DATABASE_URI'] = app.config['ADMIN_SQLALCHEMY_DATABASE_URI']
app.secret_key = app.config["SECRET_KEY"]

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "users.login"

CORS(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)
