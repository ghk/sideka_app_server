from flask import Blueprint, jsonify, request
from tatakelola import db
from tatakelola.models import PendudukModelSchemaIso
from tatakelola.repository import PendudukRepository
from tatakelola.helpers import QueryHelper

app = Blueprint('penduduk', __name__)
penduduk_repository = PendudukRepository(db)


@app.route('/penduduks', methods=['GET'])
def get_penduduks():
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = penduduk_repository.all(page_sort_params)
    result = PendudukModelSchemaIso(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/penduduks/count', methods=['GET'])
def get_penduduks_count():
    result = penduduk_repository.count()
    return jsonify(result)


@app.route('/penduduks/region/<string:region_id>', methods=['GET'])
def get_penduduks_by_region(region_id):
    entities = penduduk_repository.get_by_region(region_id)
    result = PendudukModelSchemaIso(many=True).dump(entities)
    return jsonify(result.data)
