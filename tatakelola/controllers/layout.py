from flask import Blueprint, jsonify, current_app
from tatakelola import db
from tatakelola.models import LayoutModelSchema
from tatakelola.repository import LayoutRepository

app = Blueprint('layout', __name__)
layout_repository = LayoutRepository(db)

@app.route('/layout/region/<string:region_id>', methods=['GET'])
def get_layouts_by_region(region_id):
    entities = layout_repository.get_by_region(region_id)
    result = LayoutModelSchema(many=False).dump(entities)
    return jsonify(result.data)

@app.route('/layout/prefix/<string:prefix>', methods=['GET'])
def get_by_region_prefix(prefix):
    entities = layout_repository.get_by_region_prefix(prefix)
    result = LayoutModelSchema(many=True).dump(entities)
    return jsonify(result.data)