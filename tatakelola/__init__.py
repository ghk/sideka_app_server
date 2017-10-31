import sys
sys.path.append('../common')

from flask import Flask
from flask_cors import CORS
from common.database import db
from common.marshmallow import ma

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../common/app.cfg')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['TATAKELOLA_SQLALCHEMY_DATABASE_URI'];

    # binds mean that tables with bind_key will fetch from below uris
    app.config['SQLALCHEMY_BINDS'] = {'sideka': app.config['ADMIN_SQLALCHEMY_DATABASE_URI']}
    db.init_app(app)
    ma.init_app(app)
    CORS(app)

    with app.app_context():
        # bind=None means that only main database is auto-created
        db.create_all(bind=None)

    return app


