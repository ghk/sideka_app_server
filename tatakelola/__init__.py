import sys
sys.path.append('../common')

from flask import Flask
from flask_cors import CORS
from flask_compress import Compress
from common.database import db
from common.marshmallow import ma
from controllers import *
from helpers import *

def create_app():
    app = Flask('tatakelola')
    Compress(app)
    app.config.from_pyfile('../common/app.cfg')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['TATAKELOLA_SQLALCHEMY_DATABASE_URI']

    # binds mean that tables with bind_key will fetch from below uris
    app.config['SQLALCHEMY_BINDS'] = {
        'sideka': app.config['ADMIN_SQLALCHEMY_DATABASE_URI'],
        'keuangan': app.config['KEUANGAN_SQLALCHEMY_DATABASE_URI']
    }

    app.register_blueprint(AdminController)
    app.register_blueprint(ApbdesController)
    app.register_blueprint(GeojsonController)
    app.register_blueprint(PendudukController)
    app.register_blueprint(RegionController)
    app.register_blueprint(SummaryController)
    app.register_blueprint(StatisticController)
    app.register_blueprint(LayoutController)
    app.register_blueprint(BoundaryController)
    app.register_blueprint(PostController)
    db.init_app(app)
    ma.init_app(app)
    CORS(app)

    with app.app_context():
        # bind=None means that only main database is auto-created
        db.create_all(bind=None)

    return app


