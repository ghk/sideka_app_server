from flask import Blueprint, jsonify, request
from keuangan import db
from keuangan.models import SiskeudesPenerimaanModelSchema, SiskeudesPenerimaanModelSchemaIso, \
    SiskeudesPenerimaanRinciModelSchema
from keuangan.repository import SiskeudesPenerimaanRepository, SiskeudesPenerimaanRinciRepository
from keuangan.helpers import QueryHelper, SiskeudesFetcher

app = Blueprint('penerimaan', __name__)
siskeudes_penerimaan_repository = SiskeudesPenerimaanRepository(db)
siskeudes_penerimaan_rinci_repository = SiskeudesPenerimaanRinciRepository(db)


@app.route('/siskeudes/penerimaans/year/<string:year>', methods=['GET'])
def get_siskeudes_penerimaans_by_year(year):
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    is_lokpri = request.args.get('is_lokpri', default=True, type=bool)
    entities = siskeudes_penerimaan_repository.all_by_year(year, is_lokpri, page_sort_params)
    result = SiskeudesPenerimaanModelSchemaIso(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/penerimaans/year/<string:year>/count', methods=['GET'])
def get_siskeudes_penerimaans_count_by_year(year):
    is_lokpri = request.args.get('is_lokpri', default=True, type=bool)
    result = siskeudes_penerimaan_repository.count_by_year(year, is_lokpri)
    return jsonify(result)


@app.route('/siskeudes/penerimaans/region/<string:region_id>/year/<string:year>', methods=['GET'])
def get_siskeudes_penerimaans_by_region_and_year(region_id, year):
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = siskeudes_penerimaan_repository.get_by_region_and_year(region_id, year, page_sort_params)
    result = SiskeudesPenerimaanModelSchemaIso(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/penerimaans/rincis/year/<string:year>', methods=['GET'])
def get_siskeudes_penerimaan_rincis_by_year(year):
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    is_lokpri = request.args.get('is_lokpri', default=True, type=bool)
    entities = siskeudes_penerimaan_rinci_repository.all_by_year(year, is_lokpri, page_sort_params)
    result = SiskeudesPenerimaanRinciModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/penerimaans/rincis/year/<string:year>/count', methods=['GET'])
def get_siskeudes_penerimaan_rincis_count_by_year(year):
    is_lokpri = request.args.get('is_lokpri', default=True, type=bool)
    result = siskeudes_penerimaan_rinci_repository.count_by_year(year, is_lokpri)
    return jsonify(result)


@app.route('/siskeudes/penerimaans/rincis/region/<string:region_id>/year/<string:year>', methods=['GET'])
def get_siskeudes_penerimaan_rincis_by_region_and_year(region_id, year):
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = siskeudes_penerimaan_rinci_repository.get_by_region_and_year(region_id, year, page_sort_params)
    result = SiskeudesPenerimaanRinciModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/penerimaans/fetch', methods=['GET'])
def fetch_siskeudes_penerimaans():
    SiskeudesFetcher.fetch_penerimaans()
    db.session.commit()
    return jsonify({'success': True})
