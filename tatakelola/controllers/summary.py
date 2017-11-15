from flask import Blueprint, jsonify, request
from tatakelola import db
from tatakelola.models import SummaryModelSchema
from tatakelola.repository import SummaryRepository
from tatakelola.helpers import QueryHelper

app = Blueprint('summary', __name__)
summary_repository = SummaryRepository(db)


@app.route('/summaries', methods=['GET'])
def get_penduduks():
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = summary_repository.all(page_sort_params)
    result = SummaryModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/summaries/count', methods=['GET'])
def get_penduduks_count():
    result = summary_repository.count()
    return jsonify(result)


@app.route('/summaries/region/<string:region_id>', methods=['GET'])
def get_penduduks_by_region(region_id):
    entities = summary_repository.get_by_region(region_id)
    result = SummaryModelSchema(many=True).dump(entities)
    return jsonify(result.data)
