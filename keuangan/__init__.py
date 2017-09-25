import sys
sys.path.append('../common')

from flask import Flask
from flask_cors import CORS
from common.database import db
from common.marshmallow import ma
from controllers import RegionController, ProgressController, SpendingController


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../common/app.cfg')
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['KEUANGAN_SQLALCHEMY_DATABASE_URI'];
    app.config['SQLALCHEMY_BINDS'] = { 'sideka': app.config['ADMIN_SQLALCHEMY_DATABASE_URI'] }
    app.register_blueprint(RegionController)
    app.register_blueprint(ProgressController)
    app.register_blueprint(SpendingController)
    db.init_app(app)
    ma.init_app(app)
    CORS(app)
    with app.app_context():
        db.create_all(bind=None)
    return app


