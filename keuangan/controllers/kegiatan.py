from flask import Blueprint, jsonify, request
from keuangan import db, cache
from keuangan.models import SiskeudesKegiatanModelSchema
from keuangan.repository import SiskeudesKegiatanRepository
from keuangan.helpers import QueryHelper

app = Blueprint('kegiatan', __name__)
siskeudes_kegiatan_repository = SiskeudesKegiatanRepository(db)


@app.route('/siskeudes/kegiatans/year/<string:year>', methods=['GET'])
@cache.cached(timeout=1800, query_string=True)
def get_siskeudes_kegiatans_by_year(year):
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    is_lokpri = request.args.get('is_lokpri', default=True, type=bool)
    entities = siskeudes_kegiatan_repository.all_by_year(year, is_lokpri, page_sort_params)
    result = SiskeudesKegiatanModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/kegiatans/year/<string:year>/count', methods=['GET'])
@cache.cached(timeout=1800, query_string=True)
def get_siskeudes_kegiatans_count_by_year(year):
    is_lokpri = request.args.get('is_lokpri', default=True, type=bool)
    result = siskeudes_kegiatan_repository.count_by_year(year, is_lokpri)
    return jsonify(result)


@app.route('/siskeudes/kegiatans/region/<string:region_id>/year/<string:year>', methods=['GET'])
@cache.cached(timeout=1800, query_string=True)
def get_siskeudes_kegiatans_by_region_and_year(region_id, year):
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = siskeudes_kegiatan_repository.get_by_region_and_year(region_id, year, page_sort_params)
    result = SiskeudesKegiatanModelSchema(many=True).dump(entities)
    return jsonify(result.data)
