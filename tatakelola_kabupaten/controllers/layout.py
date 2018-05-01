from flask import Blueprint, jsonify, current_app
from tatakelola_kabupaten import db
from tatakelola_kabupaten.models import LayoutModelSchema
from tatakelola_kabupaten.repository import LayoutRepository

app = Blueprint('layout', __name__)
layout_repository = LayoutRepository(db)

@app.route('/layout/region/<string:region_id>', methods=['GET'])
def get_layouts_by_region(region_id):
    entities = layout_repository.get_by_region(region_id)
    result = LayoutModelSchema(many=False).dump(entities)
    return jsonify(result.data)