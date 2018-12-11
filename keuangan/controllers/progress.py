from flask import Blueprint, jsonify, request
from keuangan import db, cache
from keuangan.models import ProgressRecapitulationModelSchema, ProgressTimelineModelSchema
from keuangan.repository import ProgressRecapitulationRepository, ProgressTimelineRepository
from keuangan.helpers import QueryHelper

app = Blueprint('progress', __name__)
progress_recapitulation_repository = ProgressRecapitulationRepository(db)
progress_timeline_repository = ProgressTimelineRepository(db)


@app.route('/progress/recapitulations/year/<string:year>', methods=['GET'])
@cache.cached(timeout=1800, query_string=True)
def get_progress_recapitulations_by_year(year):
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    kabupaten = request.args.get('kabupaten', default="33.25", type=str)
    region_id = request.args.get('region_id', default=None, type=str)
    entities = None
    if region_id is None:
        entities = progress_recapitulation_repository.all_by_kabupaten(year, kabupaten, page_sort_params)
    else:
        entities = progress_recapitulation_repository.get_by_region_and_year(region_id, year, page_sort_params)
    result = ProgressRecapitulationModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/progress/recapitulations/year/<string:year>/count', methods=['GET'])
@cache.cached(timeout=1800, query_string=True)
def get_progress_recapitulations_count_by_year(year):
    kabupaten = request.args.get('kabupaten', default="33.25", type=str)
    result = progress_recapitulation_repository.count_by_kabupaten(year, kabupaten)
    return jsonify(result)


@app.route('/progress/timelines/year/<string:year>', methods=['GET'])
@cache.cached(timeout=1800, query_string=True)
def get_progress_timelines_by_year(year):
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    kabupaten = request.args.get('kabupaten', default="33.25", type=str)
    entities = progress_timeline_repository.all_by_kabupaten(year, kabupaten, page_sort_params)
    result = ProgressTimelineModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/progress/timelines/year/<string:year>/count', methods=['GET'])
@cache.cached(timeout=1800, query_string=True)
def get_progress_timelines_count_by_year(year):
    kabupaten = request.args.get('kabupaten', default="33.25", type=str)
    result = progress_timeline_repository.count_by_kabupaten(year, kabupaten)
    return jsonify(result)


@app.route('/progress/timelines/region/<string:region_id>/year/<string:year>', methods=['GET'])
@cache.cached(timeout=1800, query_string=True)
def get_progress_timelines_by_region_and_year(region_id, year):
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = progress_timeline_repository.get_by_region_and_year(region_id, year, page_sort_params)
    result = ProgressTimelineModelSchema(many=True).dump(entities)
    return jsonify(result.data)
