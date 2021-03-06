import sys

sys.path.append('../common')

from flask import Flask
from flask_cors import CORS
from common.database import db
from common.marshmallow import ma
from controllers import *


def create_app():
    app = Flask('posyandu')

    app.config.from_pyfile('../common/app.cfg')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['POSYANDU_SQLALCHEMY_DATABASE_URI']

    # binds mean that tables with bind_key will fetch from below uris
    app.config['SQLALCHEMY_BINDS'] = {'sideka': app.config['ADMIN_SQLALCHEMY_DATABASE_URI']}

    app.register_blueprint(UserController)
    app.register_blueprint(ParentController)
    app.register_blueprint(ChildController)
    app.register_blueprint(GrowthController)
    app.register_blueprint(DevelopmentController)
    app.register_blueprint(VaccineController)

    db.init_app(app)
    ma.init_app(app)
    CORS(app)

    with app.app_context():
        # bind=None means that only main database is auto-created
        db.create_all(bind=None)

    return app
