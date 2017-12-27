from flask import Blueprint, jsonify, request
from posyandu import db
from posyandu.helpers import ResponseHelper
from posyandu.models import Growth, GrowthModelSchema

app = Blueprint('growth', __name__)


@app.route('/growths/register', methods=['POST'])
def register_growth():
    posted_growth = request.get_json(silent=True)
    if posted_growth is None:
        response = ResponseHelper.get_response(400, 'Invalid growth')
        return jsonify(response)

    result = GrowthModelSchema(many=False).load(posted_growth)
    if len(result.errors) > 0:
        response = ResponseHelper.get_response(400, 'Invalid growth')
        return jsonify(response)

    growth = result.data

    existing_growth = db.session.query(Growth) \
        .filter(Growth.month == growth.month and Growth.fk_child_id == growth.fk_child_id) \
        .first()
    if existing_growth is not None:
        response = ResponseHelper.get_already_exist_response(400, growth.month)
        return jsonify(response)

    db.session.add(growth)
    db.session.commit()

    response_data = GrowthModelSchema(many=False).dump(growth)
    response = ResponseHelper.get_response(200, 'Growth registered', response_data.data)
    return jsonify(response)
