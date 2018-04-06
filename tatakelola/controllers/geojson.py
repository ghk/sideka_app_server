from flask import Blueprint, jsonify, current_app
from tatakelola import db
from tatakelola.models import GeojsonModelSchema
from tatakelola.repository import GeojsonRepository

app = Blueprint('geojson', __name__)
geojson_repository = GeojsonRepository(db)

@app.route('/geojsons/region/<string:region_id>', methods=['GET'])
def get_geojsons_by_region_id(region_id):
    entities = geojson_repository.get_by_region(region_id)
    result = GeojsonModelSchema(many=True).dump(entities)
    return jsonify(result.data)

@app.route('/geojsons/type/<string:type>', methods=['GET'])
def get_geojsons_boundary(type):
    entities = geojson_repository.get_by_type(type)
    result = GeojsonModelSchema(many=True).dump(entities)
    return jsonify(result.data)

@app.route('/geojsons/type/<string:type>/region/<string:region_id>', methods=['GET'])
def get_geojson_by_type_and_region_id(type, region_id):
    entity = geojson_repository.get_by_type_and_region(type, region_id)
    result = GeojsonModelSchema(many=False).dump(entity)
    return jsonify(result.data)
