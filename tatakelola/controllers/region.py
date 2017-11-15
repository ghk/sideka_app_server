from flask import Blueprint, jsonify, request
from tatakelola import db
from tatakelola.models import RegionModelSchema, RegionCompleteModelSchema
from tatakelola.repository import RegionRepository
from tatakelola.helpers import QueryHelper

app = Blueprint('region', __name__)
region_repository = RegionRepository(db)


@app.route('/regions', methods=['GET'])
def get_regions():
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = region_repository.all(page_sort_params=page_sort_params)
    result = RegionModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/regions/count', methods=['GET'])
def get_regions_count():
    result = region_repository.count()
    return jsonify(result)


@app.route('/regions/<string:id>', methods=['GET'])
def get_region(id):
    region = region_repository.get(id)
    result = RegionCompleteModelSchema(many=False).dump(region)
    return jsonify(result.data)
