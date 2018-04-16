import sys, os

moddir = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
sys.path.append(moddir)

from keuangan import create_app, db
from keuangan import db
from keuangan.helpers import SiskeudesFetcher
from time import time

app = create_app()
db.app=app
db.init_app(app)

def fetch_all(year):
    SiskeudesFetcher.fetch_desas()
    SiskeudesFetcher.fetch_siskeudes_codes_by_year(year)
    SiskeudesFetcher.fetch_penerimaans_by_year(year)
    SiskeudesFetcher.fetch_penganggarans_by_year(year)
    SiskeudesFetcher.fetch_spps_by_year(year)

    db.session.commit()

def generate_all(year):
    prs = Generator.generate_progress_recapitulations_by_year(year)
    pts = Generator.generate_progress_timelines_by_year(year)
    srs = Generator.generate_budget_recapitulations_by_year(year)
    sls = Generator.generate_siskeudes_likelihood_by_year(year)

    # TODO: Improve speed by using bulk_save_objects
    db.session.add_all(prs)
    db.session.add_all(pts)
    db.session.add_all(srs)
    db.session.add_all(sls)
    db.session.commit()

if __name__ == '__main__':
    fetch_all("2017")
    generate_all("2017")