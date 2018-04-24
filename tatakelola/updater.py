import sys, os

moddir = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
sys.path.append(moddir)
sys.path.append('../common')

from tatakelola import create_app
from tatakelola import db
from tatakelola.helpers import TatakelolaFetcher, Generator
from time import time

app = create_app()
db.init_app(app)

def fetch_all():
    TatakelolaFetcher.fetch_desas()
    TatakelolaFetcher.fetch_geojsons()
    #TatakelolaFetcher.fetch_data()
    TatakelolaFetcher.fetch_penduduks()
    TatakelolaFetcher.fetch_apbdes()
    db.session.commit()

def generate_all():
    summaries = Generator.generate_summaries()
    layouts = Generator.generate_layouts()
    boundary = Generator.generate_boundaries()

    db.session.add(boundary)
    db.session.add_all(layouts)
    db.session.add_all(summaries)
    db.session.commit()

with app.app_context():
    fetch_all()
    generate_all()