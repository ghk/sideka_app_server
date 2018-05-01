from flask import Blueprint, jsonify, request
from tatakelola_kabupaten import db
from tatakelola_kabupaten.models import SummaryModelSchema
from tatakelola_kabupaten.repository import SummaryRepository
from common.helpers import QueryHelper

app = Blueprint('summary', __name__)
summary_repository = SummaryRepository(db)


@app.route('/summaries/get_all/<string:kabupaten_code>', methods=['GET'])
def get_summaries(kabupaten_code):
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    
    entities = summary_repository.get_all_by_kabupaten(kabupaten_code, page_sort_params)
    result = SummaryModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/summaries/count/<string:kabupaten_code>', methods=['GET'])
def get_summaries_count(kabupaten_code):
    result = summary_repository.count_kabupaten(kabupaten_code)
    return jsonify(result)


@app.route('/summaries/region/<string:region_id>', methods=['GET'])
def get_summaries_by_region(region_id):
    entities = summary_repository.get_by_region(region_id)
    result = SummaryModelSchema(many=True).dump(entities)
    return jsonify(result.data)