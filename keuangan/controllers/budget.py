from flask import Blueprint, jsonify, request
from keuangan import db
from keuangan.models import BudgetTypeModelSchema, BudgetRecapitulationModelSchema, \
    BudgetRecapitulationCompleteModelSchema
from keuangan.repository import RegionRepository, BudgetTypeRepository, BudgetRecapitulationRepository
from keuangan.helpers import QueryHelper, Generator

app = Blueprint('budget', __name__)

region_repository = RegionRepository(db)
budget_type_repository = BudgetTypeRepository(db)
budget_recapitulation_repository = BudgetRecapitulationRepository(db)


@app.route('/budget/types', methods=['GET'])
def get_budget_types():
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)

    is_revenue = request.args.get('is_revenue')
    if (is_revenue and is_revenue == 'true'):
        is_revenue = True
    else:
        is_revenue = False

    entities = budget_type_repository.all_by_condition(is_revenue=is_revenue, page_sort_params=page_sort_params)
    result = BudgetTypeModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/budget/types/generate', methods=['GET'])
def generate_budget_types():
    budget_types = Generator.generate_budget_types()
    db.session.add_all(budget_types)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/budget/recapitulations/year/<string:year>', methods=['GET'])
def get_budget_recapitulations_by_year(year):
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)

    is_lokpri = request.args.get('is_lokpri', default=True, type=bool)
    entities = budget_recapitulation_repository.all_by_year(year, is_lokpri, page_sort_params)

    is_full_region = request.args.get('is_full_region', default=True, type=bool)
    if is_full_region:
        result = BudgetRecapitulationCompleteModelSchema(many=True).dump(entities)
    else:
        result = BudgetRecapitulationModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/budget/recapitulations/year/<string:year>/count', methods=['GET'])
def get_budget_recapitulations_count_by_year(year):
    is_lokpri = request.args.get('is_lokpri', default=True, type=bool)
    result = budget_recapitulation_repository.count_by_year(year, is_lokpri)
    return jsonify(result)


@app.route('/budget/recapitulations/region/<string:region_id>/year/<string:year>', methods=['GET'])
def get_budget_recapitulations_by_region_and_year(region_id, year):
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = budget_recapitulation_repository.get_by_region_and_year(region_id, year, page_sort_params)
    result = BudgetRecapitulationModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/budget/recapitulations/generate', methods=['GET'])
def generate_budget_recapitulations():
    entities = Generator.generate_budget_recapitulations()
    db.session.add_all(entities)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/budget/recapitulations/region/<string:region_id>/generate', methods=['GET'])
def generate_budget_recapitulations_by_region(region_id):
    region = region_repository.get(region_id)
    entities = Generator.generate_budget_recapitulation_by_region(region)
    db.session.add_all(entities)
    db.session.commit()
    return jsonify({'success': True})
