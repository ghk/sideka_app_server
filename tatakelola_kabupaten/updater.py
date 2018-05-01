import sys, os

moddir = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
sys.path.append(moddir)
sys.path.append('../common')

from tatakelola_kabupaten import create_app
from tatakelola_kabupaten import db
from tatakelola_kabupaten.helpers import TatakelolaKabupatenFetcher, Generator
from time import time

app = create_app()
db.init_app(app)

def fetch_all():
    TatakelolaKabupatenFetcher.fetch_desas("18.05")
    TatakelolaKabupatenFetcher.fetch_data("18.05")
    TatakelolaKabupatenFetcher.fetch_geojsons("18.05")
    TatakelolaKabupatenFetcher.fetch_apbdes("18.05")
    db.session.commit()

def generate_all():
    summaries = Generator.generate_summaries("18.05")
    layouts = Generator.generate_layouts("18.05")
    boundary = Generator.generate_boundaries("18.05")

    db.session.add(boundary)
    db.session.add_all(layouts)
    db.session.add_all(summaries)
    db.session.commit()
with app.app_context():
    fetch_all()
    generate_all()