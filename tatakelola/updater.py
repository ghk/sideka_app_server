import sys, os

moddir = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
sys.path.append(moddir)

from tatakelola import create_app, db
from tatakelola import db
from tatakelola.helpers import TatakelolaFetcher, Generator
<<<<<<< HEAD
from tatakelola.repository import BoundaryRepository
=======
>>>>>>> 0a66df83d2c3b51aee9c2613d3f56123359b63cf
from time import time

app = create_app()
db.app=app
db.init_app(app)

supradesa_code = 'lokpri'
boundary_repository = BoundaryRepository(db)

if len(sys.argv) > 1:
    supradesa_code = sys.argv[1]

def fetch_all():
    print "Fetching desas..."
    TatakelolaFetcher.fetch_desas()

    print "Fetching GeoJSONs..."
    TatakelolaFetcher.fetch_geojsons(supradesa_code)

    print "Fetching data..."
    TatakelolaFetcher.fetch_data(supradesa_code)

    print "Fetching APBDeses..."
    TatakelolaFetcher.fetch_apbdes(supradesa_code)
    
    db.session.commit()

def generate_all():
    print "Generating summaries..."
    summaries = Generator.generate_summaries(supradesa_code)

    print "Generating layouts..."
    layouts = Generator.generate_layouts(supradesa_code)

    print "Deleting previous boundaries..."
    prev_boundary = boundary_repository.get_by_supradesa_code(supradesa_code)
    
    print "Generating boundaries..."
    boundary = Generator.generate_boundaries(supradesa_code)

    db.session.add(boundary)
    db.session.add_all(layouts)
    db.session.add_all(summaries)
    db.session.delete(prev_boundary)

    db.session.commit()

if __name__ == '__main__':
    #fetch_all()
    generate_all()
