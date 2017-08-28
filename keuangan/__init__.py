import sys
sys.path.append('../common')

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('../common/app.cfg')
app.config['SQLALCHEMY_DATABASE_URI'] = app.config['KEUANGAN_SQLALCHEMY_DATABASE_URI'];
db = SQLAlchemy(app)