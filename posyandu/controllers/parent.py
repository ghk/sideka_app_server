from flask import Blueprint, jsonify, request
from posyandu import db
from posyandu.helpers import ResponseHelper
from posyandu.models import Parent, ParentModelSchema

app = Blueprint('parent', __name__)


@app.route('/parents/register', methods=['POST'])
def register_parent():
    posted_parent = request.get_json(silent=True)
    if posted_parent is None:
        response = ResponseHelper.get_response(400, 'Invalid parent')
        return jsonify(response)

    result = ParentModelSchema(many=False).load(posted_parent)
    if len(result.errors) > 0:
        response = ResponseHelper.get_response(400, 'Invalid parent')
        return jsonify(response)

    parent = result.data

    existing_parent = db.session.query(Parent) \
        .filter(Parent.name == parent.name) \
        .first()
    if existing_parent is not None:
        response = ResponseHelper.get_already_exist_response(400, parent.name)
        return jsonify(response)

    db.session.add(parent)
    db.session.commit()

    response_data = ParentModelSchema(many=False).dump(parent)
    response = ResponseHelper.get_response(200, 'Parent registered', response_data.data)
    return jsonify(response)
