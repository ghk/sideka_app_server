from flask import Blueprint, jsonify, request
from posyandu import db
from posyandu.helpers import ResponseHelper
from posyandu.models import Development, DevelopmentModelSchema

app = Blueprint('development', __name__)


@app.route('/developments/register', methods=['POST'])
def register_development():
    posted_development = request.get_json(silent=True)
    if posted_development is None:
        response = ResponseHelper.get_response(400, 'Invalid development')
        return jsonify(response)

    result = DevelopmentModelSchema(many=False).load(posted_development)
    if len(result.errors) > 0:
        response = ResponseHelper.get_response(400, 'Invalid development')
        return jsonify(response)

    development = result.data

    existing_development = db.session.query(Development) \
        .filter(Development.month == development.month and Development.fk_child_id == development.fk_child_id) \
        .first()
    if existing_development is not None:
        response = ResponseHelper.get_already_exist_response(400, development.month)
        return jsonify(response)

    db.session.add(development)
    db.session.commit()

    response_data = DevelopmentModelSchema(many=False).dump(development)
    response = ResponseHelper.get_response(200, 'Development registered', response_data.data)
    return jsonify(response)
