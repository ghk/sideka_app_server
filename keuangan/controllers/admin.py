from flask import Blueprint, jsonify, current_app
from time import time
from keuangan import db
from keuangan.helpers import SiskeudesFetcher, Generator, SiskeudesPenganggaranTransformer
from keuangan.repository import SiskeudesPenganggaranRepository
from keuangan.models import SiskeudesPenganggaranModelSchema

app = Blueprint('admin', __name__)
spr = SiskeudesPenganggaranRepository(db)


@app.route('/admin/fetch/desas', methods=['GET'])
def fetch_desa_ids():
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
    SiskeudesFetcher.fetch_desas()
    SiskeudesFetcher.fetch_siskeudes_codes()
    SiskeudesFetcher.fetch_penerimaans()
    SiskeudesFetcher.fetch_penganggarans()
    SiskeudesFetcher.fetch_spps()
    db.session.commit()
    current_app.logger.info('Fetch Total Time: ' + str(time() - t0) + ' seconds')
    return jsonify({'success': True})


@app.route('/admin/generate/all', methods=['GET'])
def generate_all():
    t0 = time()
    prs = Generator.generate_progress_recapitulations()
    pts = Generator.generate_progress_timelines()
    srs = Generator.generate_budget_recapitulations()

    # TODO: Improve speed by using bulk_save_objects
    db.session.add_all(prs)
    db.session.add_all(pts)
    db.session.add_all(srs)
    db.session.commit()
    current_app.logger.info('Generate Total Time: ' + str(time() - t0) + ' seconds')
    return jsonify({'success': True})


@app.route('/admin/run/all', methods=['GET'])
def run_all():
    fetch_result = fetch_all()
    generate_result = generate_all()
    return generate_result;
