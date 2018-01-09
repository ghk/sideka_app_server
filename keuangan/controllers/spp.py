from flask import Blueprint, jsonify, request
from keuangan import db, cache
from keuangan.models import SiskeudesSppModelSchema, SiskeudesSppBuktiModelSchema, SiskeudesSppRinciModelSchema
from keuangan.models import SiskeudesSppModelSchemaIso, SiskeudesSppBuktiModelSchemaIso
from keuangan.repository import SiskeudesSppRepository, SiskeudesSppBuktiRepository, SiskeudesSppRinciRepository
from keuangan.helpers import QueryHelper

app = Blueprint('spp', __name__)
siskeudes_spp_repository = SiskeudesSppRepository(db)
siskeudes_spp_bukti_repository = SiskeudesSppBuktiRepository(db)
siskeudes_spp_rinci_repository = SiskeudesSppRinciRepository(db)


@app.route('/siskeudes/spps/year/<string:year>', methods=['GET'])
@cache.cached(timeout=1800, query_string=True)
def get_siskeudes_spps_by_year(year):
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    is_lokpri = request.args.get('is_lokpri', default=True, type=bool)
    entities = siskeudes_spp_repository.all_by_year(year, is_lokpri, page_sort_params)
    result = SiskeudesSppModelSchemaIso(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/spps/year/<string:year>/count', methods=['GET'])
@cache.cached(timeout=1800, query_string=True)
def get_siskeudes_spps_count_by_year(year):
    is_lokpri = request.args.get('is_lokpri', default=True, type=bool)
    result = siskeudes_spp_repository.count_by_year(year, is_lokpri)
    return jsonify(result)


@app.route('/siskeudes/spps/region/<string:region_id>/year/<string:year>', methods=['GET'])
@cache.cached(timeout=1800, query_string=True)
def get_siskeudes_spps_by_region(region_id, year):
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = siskeudes_spp_repository.get_by_region_and_year(region_id, year, page_sort_params)
    result = SiskeudesSppModelSchemaIso(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/spps/buktis/year/<string:year>', methods=['GET'])
@cache.cached(timeout=1800, query_string=True)
def get_siskeudes_spps_buktis_by_year(year):
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    is_lokpri = request.args.get('is_lokpri', default=True, type=bool)
    entities = siskeudes_spp_bukti_repository.all_by_year(year, is_lokpri, page_sort_params)
    result = SiskeudesSppBuktiModelSchemaIso(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/spps/buktis/year/<string:year>/count', methods=['GET'])
@cache.cached(timeout=1800, query_string=True)
def get_siskeudes_spps_buktis_count_by_year(year):
    is_lokpri = request.args.get('is_lokpri', default=True, type=bool)
    result = siskeudes_spp_bukti_repository.count_by_year(year, is_lokpri)
    return jsonify(result)


@app.route('/siskeudes/spps/buktis/region/<string:region_id>/year/<string:year>', methods=['GET'])
@cache.cached(timeout=1800, query_string=True)
def get_siskeudes_spps_buktis_by_region_and_year(region_id, year):
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = siskeudes_spp_bukti_repository.get_by_region_and_year(region_id, year, page_sort_params)
    result = SiskeudesSppBuktiModelSchemaIso(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/spps/rincis/year/<string:year>', methods=['GET'])
@cache.cached(timeout=1800, query_string=True)
def get_siskeudes_spps_rincis_by_year(year):
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    is_lokpri = request.args.get('is_lokpri', default=True, type=bool)
    entities = siskeudes_spp_rinci_repository.all_by_year(year, is_lokpri, page_sort_params)
    result = SiskeudesSppRinciModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/spps/rincis/year/<string:year>/count', methods=['GET'])
@cache.cached(timeout=1800, query_string=True)
def get_siskeudes_spps_rincis_count_by_year(year):
    is_lokpri = request.args.get('is_lokpri', default=True, type=bool)
    result = siskeudes_spp_rinci_repository.count_by_year(year, is_lokpri)
    return jsonify(result)


@app.route('/siskeudes/spps/rincis/region/<string:region_id>/year/<string:year>', methods=['GET'])
@cache.cached(timeout=1800, query_string=True)
def get_siskeudes_spps_rincis_by_region_and_year(region_id, year):
    entities = siskeudes_spp_rinci_repository.get_by_region_and_year(region_id, year)
    result = SiskeudesSppRinciModelSchema(many=True).dump(entities)
    return jsonify(result.data)
