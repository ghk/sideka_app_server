from flask import Blueprint, jsonify, request
from keuangan import db
from keuangan.helpers import SiskeudesFetcher, Generator

app = Blueprint('admin', __name__)


@app.route('/admin/fetch/all', methods=['GET'])
def fetch_all():
    SiskeudesFetcher.fetch_penerimaans()
    SiskeudesFetcher.fetch_penganggarans()
    SiskeudesFetcher.fetch_spps()
    return jsonify({'success': True})


@app.route('/admin/generate/all', methods=['GET'])
def generate_all():
    prs = Generator.generate_progress_recapitulations()
    pts = Generator.generate_progress_timelines()
    srs = Generator.generate_spending_recapitulations()
    db.session.add_all(prs)
    db.session.add_all(pts)
    db.session.add_all(srs)
    db.session.commit()
    return jsonify({'success': True})
