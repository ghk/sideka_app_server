from flask import Blueprint, jsonify, request
from posyandu import db
from posyandu.helpers import ResponseHelper
from posyandu.models import Vaccine, VaccineModelSchema

app = Blueprint('vaccine', __name__)


@app.route('/vaccines/register', methods=['POST'])
def register_vaccine():
    posted_vaccine = request.get_json(silent=True)
    if posted_vaccine is None:
        response = ResponseHelper.get_response(400, 'Invalid vaccine')
        return jsonify(response)

    result = VaccineModelSchema(many=False).load(posted_vaccine)
    if len(result.errors) > 0:
        response = ResponseHelper.get_response(400, 'Invalid vaccine')
        return jsonify(response)

    vaccine = result.data

    existing_vaccine = db.session.query(Vaccine) \
        .filter(Vaccine.name == vaccine.name and Vaccine.fk_child_id == vaccine.fk_child_id and Vaccine.fk_growth_id == vaccine.fk_growth_id) \
        .first()
    if existing_vaccine is not None:
        response = ResponseHelper.get_already_exist_response(400, vaccine.name)
        return jsonify(response)

    db.session.add(vaccine)
    db.session.commit()

    response_data = VaccineModelSchema(many=False).dump(vaccine)
    response = ResponseHelper.get_response(200, 'Vaccine registered', response_data.data)
    return jsonify(response)
