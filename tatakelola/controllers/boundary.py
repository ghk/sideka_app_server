from flask import Blueprint, jsonify, current_app
from tatakelola import db
from tatakelola.models import BoundaryModelSchema
from tatakelola.repository import BoundaryRepository

app = Blueprint('boundary', __name__)
boundary_repository = BoundaryRepository(db)

@app.route('/boundary/all', methods=['GET'])
def get_boundaries():
    entities = boundary_repository.get()
    result = BoundaryModelSchema(many=False).dump(entities)
    return jsonify(result.data)