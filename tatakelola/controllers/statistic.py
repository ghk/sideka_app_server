from flask import Blueprint, jsonify, request
from tatakelola import db
from tatakelola.models import StatisticModelSchema
from tatakelola.repository import StatisticRepository
from tatakelola.helpers import QueryHelper

app = Blueprint('statistic', __name__)
statistic_repository = StatisticRepository(db)


@app.route('/statistics', methods=['GET'])
def get_statistic():
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = statistic_repository.all(page_sort_params)
    result = StatisticModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/statistics/count', methods=['GET'])
def get_statistic_count():
    result = statistic_repository.count()
    return jsonify(result)


@app.route('/statistics/region/<string:region_id>', methods=['GET'])
def get_statistic_by_region(region_id):
    entities = statistic_repository.get_by_region(region_id)
    result = StatisticModelSchema(many=True).dump(entities)
    return jsonify(result.data)

@app.route('/statistics/get_all', methods=['GET'])
def get_all():
    entities = statistic_repository.get_all()
    result = StatisticModelSchema(many=True).dump(entities)
    return jsonify(result.data)