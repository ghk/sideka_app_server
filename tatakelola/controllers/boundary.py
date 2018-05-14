from flask import Blueprint, jsonify, current_app
from tatakelola import db
from tatakelola.models import BoundaryModelSchema
from tatakelola.repository import BoundaryRepository

app = Blueprint('boundary', __name__)
boundary_repository = BoundaryRepository(db)

@app.route('/boundary/supradesa/<string:supradesa_code>', methods=['GET'])
def get_by_supradesa_code(supradesa_code):
    entity = boundary_repository.get_by_supradesa_code(supradesa_code)
    result = BoundaryModelSchema(many=False).dump(entity)
    return jsonify(result.data)