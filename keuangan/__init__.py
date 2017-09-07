import sys
sys.path.append('../common')

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config.from_pyfile('../common/app.cfg')
app.config['SQLALCHEMY_DATABASE_URI'] = app.config['KEUANGAN_SQLALCHEMY_DATABASE_URI'];
app.config['SQLALCHEMY_ECHO'] = True

CORS(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)
