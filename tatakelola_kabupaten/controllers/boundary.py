from flask import Blueprint, jsonify, current_app
from tatakelola_kabupaten import db
from tatakelola_kabupaten.models import BoundaryModelSchema
from tatakelola_kabupaten.repository import BoundaryRepository

app = Blueprint('boundary', __name__)
boundary_repository = BoundaryRepository(db)

@app.route('/boundary/all/<string:kabupaten_code>', methods=['GET'])
def get_boundaries_by_kabupaten(kabupaten_code):
    entities = boundary_repository.get(kabupaten_code)
    result = BoundaryModelSchema(many=False).dump(entities)
    return jsonify(result.data)