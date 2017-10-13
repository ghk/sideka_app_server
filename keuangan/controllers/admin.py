from flask import Blueprint, jsonify, request
from time import time
from keuangan import db
from keuangan.helpers import SiskeudesFetcher, Generator

app = Blueprint('admin', __name__)


@app.route('/admin/fetch/all', methods=['GET'])
def fetch_all():
    t0 = time()
    SiskeudesFetcher.fetch_penerimaans()
    SiskeudesFetcher.fetch_penganggarans()
    SiskeudesFetcher.fetch_spps()
    db.session.commit()
    print('\x1b[6;30;42m' + 'Total Time: ' + str(time() - t0) + ' seconds' + '\x1b[0m')
    return jsonify({'success': True})


@app.route('/admin/generate/all', methods=['GET'])
def generate_all():
    t0 = time()
    prs = Generator.generate_progress_recapitulations()
    pts = Generator.generate_progress_timelines()
    srs = Generator.generate_spending_recapitulations()

    #TODO: Improve speed by using bulk_save_objects
    db.session.add_all(prs)
    db.session.add_all(pts)
    db.session.add_all(srs)
    db.session.commit()
    print('\x1b[6;30;42m' + 'Total Time: ' + str(time() - t0) + ' seconds' + '\x1b[0m')
    return jsonify({'success': True})
