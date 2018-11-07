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

def fetch_tulang_bawang():
    TatakelolaKabupatenFetcher.fetch_desas_by_kabupaten("18.05")
    TatakelolaKabupatenFetcher.fetch_data_by_kabupaten("18.05")
    TatakelolaKabupatenFetcher.fetch_geojson_by_kabupaten("18.05")
    TatakelolaKabupatenFetcher.fetch_apbdes_by_kabupaten("18.05")
    db.session.commit()

def generate_tulang_bawang():
    summaries = Generator.generate_summaries_by_kabupaten("18.05")
    layouts = Generator.generate_layouts_by_kabupaten("18.05")
    boundary = Generator.generate_boundaries_by_kabupaten("18.05")

    db.session.add(boundary)
    db.session.add_all(layouts)
    db.session.add_all(summaries)
    db.session.commit()

def fetch_jateng_kabupatens():
    TatakelolaKabupatenFetcher.fetch_kabupatens("33")
    db.session.commit()

def fetch_jateng():
    TatakelolaKabupatenFetcher.fetch_desas_by_province("33")
    TatakelolaKabupatenFetcher.fetch_data_by_province("33")
    TatakelolaKabupatenFetcher.fetch_geojson_by_province("33")
    TatakelolaKabupatenFetcher.fetch_apbdes_by_province("33")
    db.session.commit()

def generate_jateng():
    summaries = Generator.generate_summaries_by_province("33")
    layouts = Generator.generate_layouts_by_province("33")
    boundary = Generator.generate_boundaries_by_province("33")

    db.session.add(boundary)
    db.session.add_all(layouts)
    db.session.add_all(summaries)
    db.session.commit()
   
with app.app_context():
    #fetch_jateng()
    #generate_jateng()
    
    #fetch_all()
    #generate_all()