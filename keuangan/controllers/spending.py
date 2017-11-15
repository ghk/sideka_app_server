from flask import Blueprint, jsonify, request
from keuangan import db
from keuangan.models import SpendingTypeModelSchema, SpendingRecapitulationModelSchema
from keuangan.repository import RegionRepository, SpendingTypeRepository, SpendingRecapitulationRepository
from keuangan.helpers import QueryHelper, Generator

app = Blueprint('spending', __name__)
region_repository = RegionRepository(db)

spending_type_repository = SpendingTypeRepository(db)
spending_recapitulation_repository = SpendingRecapitulationRepository(db)


@app.route('/spending/types', methods=['GET'])
def get_spending_types():
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = spending_type_repository.all(page_sort_params)
    result = SpendingTypeModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/spending/types/generate', methods=['GET'])
def generate_spending_types():
    spending_types = Generator.generate_spending_types()
    db.session.add_all(spending_types)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/spending/recapitulations', methods=['GET'])
def get_spending_recapitulations():
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = spending_recapitulation_repository.all(page_sort_params)
    result = SpendingRecapitulationModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/spending/recapitulations/count', methods=['GET'])
def get_spending_recapitulations_count():
    result = spending_recapitulation_repository.count()
    return jsonify(result)


@app.route('/spending/recapitulations/region/<string:region_id>', methods=['GET'])
def get_spending_recapitulations_by_region(region_id):
    entities = spending_recapitulation_repository.get_by_region(region_id)
    result = SpendingRecapitulationModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/spending/recapitulations/generate', methods=['GET'])
def generate_spending_recapitulations():
    spending_recapitulations = Generator.generate_spending_recapitulations()
    db.session.add_all(spending_recapitulations)
    db.session.commit()
    return jsonify({'success': True})
