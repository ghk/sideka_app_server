from flask import Blueprint, jsonify, request
from posyandu import db
from posyandu.helpers import ResponseHelper
from posyandu.models import User, UserModelSchema

app = Blueprint('user', __name__)


@app.route('/users/register', methods=['POST'])
def register_user():
    posted_user = request.get_json(silent=True)
    if posted_user is None:
        response = ResponseHelper.get_response(400, 'Invalid user')
        return jsonify(response)

    result = UserModelSchema(many=False).load(posted_user)
    if len(result.errors) > 0:
        response = ResponseHelper.get_response(400, 'Invalid user')
        return jsonify(response)

    user = result.data

    existing_user = db.session.query(User) \
        .filter(User.user_name == user.user_name) \
        .first()
    if existing_user is not None:
        response = ResponseHelper.get_already_exist_response(400, user.user_name)
        return jsonify(response)

    db.session.add(user)
    db.session.commit()

    response_data = UserModelSchema(many=False).dump(user)
    response = ResponseHelper.get_response(200, 'User registered', response_data.data)
    return jsonify(response)


@app.route('/users/<string:user_name>', methods=['GET'])
def get_user(user_name):
    user = db.session.query(User) \
        .filter(User.user_name == user_name) \
        .first()

    anu = request.args.get('anu', default=None, type=int)
    response_data = UserModelSchema(many=False).dump(user)
    response = ResponseHelper.get_response(200, '', response_data.data)
    return jsonify(response)
