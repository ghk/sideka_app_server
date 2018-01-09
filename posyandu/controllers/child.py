from flask import Blueprint, jsonify, request
from posyandu import db
from posyandu.helpers import ResponseHelper
from posyandu.models import Child, ChildModelSchema

app = Blueprint('child', __name__)


@app.route('/childs/register', methods=['POST'])
def register_child():
    posted_child = request.get_json(silent=True)
    if posted_child is None:
        response = ResponseHelper.get_response(400, 'Invalid child')
        return jsonify(response)

    result = ChildModelSchema(many=False).load(posted_child)
    if len(result.errors) > 0:
        response = ResponseHelper.get_response(400, 'Invalid child')
        return jsonify(response)

    child = result.data

    existing_child = db.session.query(Child) \
        .filter(Child.name == child.name) \
        .first()
    if existing_child is not None:
        response = ResponseHelper.get_already_exist_response(400, child.name)
        return jsonify(response)

    db.session.add(child)
    db.session.commit()

    response_data = ChildModelSchema(many=False).dump(child)
    response = ResponseHelper.get_response(200, 'Child registered', response_data.data)
    return jsonify(response)
