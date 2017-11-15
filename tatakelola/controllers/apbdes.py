from flask import Blueprint, jsonify, request
from tatakelola import db
from tatakelola.models import ApbdesModelSchema
from tatakelola.repository import ApbdesRepository
from tatakelola.helpers import QueryHelper

app = Blueprint('apbdes', __name__)
apbdes_repository = ApbdesRepository(db)


@app.route('/apbdes', methods=['GET'])
def get_apbdes():
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = apbdes_repository.all(page_sort_params)
    result = ApbdesModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/apbdes/count', methods=['GET'])
def get_apbdes_count():
    result = apbdes_repository.count()
    return jsonify(result)


@app.route('/apbdes/region/<string:region_id>', methods=['GET'])
def get_apbdes_by_region(region_id):
    entities = apbdes_repository.get_by_region(region_id)
    result = ApbdesModelSchema(many=True).dump(entities)
    return jsonify(result.data)
