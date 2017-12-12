from datetime import datetime
from flask import Blueprint, jsonify, current_app
from time import time
from keuangan import db
from keuangan.helpers import SiskeudesFetcher, Generator
from keuangan.repository import SiskeudesPenganggaranRepository

app = Blueprint('admin', __name__)
spr = SiskeudesPenganggaranRepository(db)


@app.route('/admin/fetch/desas', methods=['GET'])
def fetch_desas():
    t0 = time()
    SiskeudesFetcher.fetch_desas()
    db.session.commit()
    current_app.logger.info('Fetch Siskeudes Desa Id Total Time: ' + str(time() - t0) + ' seconds')
    return jsonify({'success': True})


@app.route('/admin/fetch/siskeudes_codes', methods=['GET'])
def fetch_siskeudes_codes():
    t0 = time()
    SiskeudesFetcher.fetch_siskeudes_codes()
    db.session.commit()
    current_app.logger.info('Fetch Siskeudes Code Total Time: ' + str(time() - t0) + ' seconds')
    return jsonify({'success': True})


@app.route('/admin/fetch/all', methods=['GET'])
def fetch_all():
    t0 = time()

    year = str(datetime.now().year)
    SiskeudesFetcher.fetch_desas()
    SiskeudesFetcher.fetch_siskeudes_codes_by_year(year)
    SiskeudesFetcher.fetch_penerimaans_by_year(year)
    SiskeudesFetcher.fetch_penganggarans_by_year(year)
    SiskeudesFetcher.fetch_spps_by_year(year)

    db.session.commit()

    current_app.logger.info('Fetch Total Time: ' + str(time() - t0) + ' seconds')
    return jsonify({'success': True})


@app.route('/admin/generate/all', methods=['GET'])
def generate_all():
    t0 = time()

    year = str(datetime.now().year)
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

    current_app.logger.info('Generate Total Time: ' + str(time() - t0) + ' seconds')
    return jsonify({'success': True})


@app.route('/admin/run/all', methods=['GET'])
def run_all():
    fetch_result = fetch_all()
    generate_result = generate_all()
    return generate_result
