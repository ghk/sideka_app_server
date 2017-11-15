from flask import Blueprint, jsonify, request
from keuangan import db
from keuangan.models import SiskeudesPenerimaanModelSchema, SiskeudesPenerimaanModelSchemaIso, SiskeudesPenerimaanRinciModelSchema
from keuangan.repository import SiskeudesPenerimaanRepository, SiskeudesPenerimaanRinciRepository
from keuangan.helpers import QueryHelper, SiskeudesFetcher

app = Blueprint('penerimaan', __name__)
siskeudes_penerimaan_repository = SiskeudesPenerimaanRepository(db)
siskeudes_penerimaan_rinci_repository = SiskeudesPenerimaanRinciRepository(db)


@app.route('/siskeudes/penerimaans', methods=['GET'])
def get_siskeudes_penerimaans():
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = siskeudes_penerimaan_repository.all(page_sort_params)
    result = SiskeudesPenerimaanModelSchemaIso(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/penerimaans/count', methods=['GET'])
def get_siskeudes_penerimaans_count():
    result = siskeudes_penerimaan_repository.count()
    return jsonify(result)


@app.route('/siskeudes/penerimaans/region/<string:region_id>', methods=['GET'])
def get_siskeudes_penerimaans_by_region(region_id):
    entities = siskeudes_penerimaan_repository.get_by_region(region_id)
    result = SiskeudesPenerimaanModelSchemaIso(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/penerimaans/fetch', methods=['GET'])
def fetch_siskeudes_penerimaans():
    SiskeudesFetcher.fetch_penerimaans()
    db.session.commit()
    return jsonify({'success': True})


@app.route('/siskeudes/penerimaans/rincis', methods=['GET'])
def get_siskeudes_penerimaan_rincis():
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = siskeudes_penerimaan_rinci_repository.all(page_sort_params)
    result = SiskeudesPenerimaanRinciModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/penerimaans/rincis/count', methods=['GET'])
def get_siskeudes_penerimaan_rincis_count():
    result = siskeudes_penerimaan_rinci_repository.count()
    return jsonify(result)


@app.route('/siskeudes/penerimaans/rincis/region/<string:region_id>', methods=['GET'])
def get_siskeudes_penerimaan_rincis_by_region(region_id):
    entities = siskeudes_penerimaan_rinci_repository.get_by_region(region_id)
    result = SiskeudesPenerimaanRinciModelSchema(many=True).dump(entities)
    return jsonify(result.data)
