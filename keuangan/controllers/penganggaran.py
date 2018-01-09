from flask import Blueprint, jsonify, request
from keuangan import db, cache
from keuangan.models import SiskeudesPenganggaranModelSchema
from keuangan.repository import SiskeudesPenganggaranRepository
from keuangan.helpers import QueryHelper

app = Blueprint('penganggaran', __name__)
siskeudes_penganggaran_repository = SiskeudesPenganggaranRepository(db)


@app.route('/siskeudes/penganggarans/year/<string:year>', methods=['GET'])
@cache.cached(timeout=1800, query_string=True)
def get_siskeudes_penganggarans_by_year(year):
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    is_lokpri = request.args.get('is_lokpri', default=True, type=bool)
    entities = siskeudes_penganggaran_repository.all_by_year(year, is_lokpri, page_sort_params)
    result = SiskeudesPenganggaranModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/penganggarans/year/<string:year>/count', methods=['GET'])
@cache.cached(timeout=1800, query_string=True)
def get_siskeudes_penganggarans_count_by_year(year):
    is_lokpri = request.args.get('is_lokpri', default=True, type=bool)
    result = siskeudes_penganggaran_repository.count_by_year(year, is_lokpri)
    return jsonify(result)


@app.route('/siskeudes/penganggarans/region/<string:region_id>/year/<string:year>', methods=['GET'])
@cache.cached(timeout=1800, query_string=True)
def get_siskeudes_penganggarans_by_region_and_year(region_id, year):
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = siskeudes_penganggaran_repository.get_by_region_and_year(region_id, year, page_sort_params)
    result = SiskeudesPenganggaranModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/penganggarans/region/<string:region_id>/year/<string:year>/spending', methods=['GET'])
@cache.cached(timeout=1800, query_string=True)
def get_siskeudes_penganggarans_total_spending_by_region_and_year(region_id, year):
    is_lokpri = request.args.get('is_lokpri', default=True, type=bool)
    result = siskeudes_penganggaran_repository.get_total_spending_by_region_and_year(region_id, year, is_lokpri)
    return jsonify(result)
