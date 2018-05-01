from flask import Blueprint, jsonify, request
from keuangan import db, cache
from keuangan.models import BudgetTypeModelSchema, BudgetRecapitulationModelSchema, \
    BudgetRecapitulationCompleteModelSchema
from keuangan.repository import RegionRepository, BudgetTypeRepository, BudgetRecapitulationRepository
from keuangan.helpers import QueryHelper

app = Blueprint('budget', __name__)
region_repository = RegionRepository(db)
budget_type_repository = BudgetTypeRepository(db)
budget_recapitulation_repository = BudgetRecapitulationRepository(db)


@app.route('/budget/types', methods=['GET'])
@cache.cached(timeout=1800, query_string=True)
def get_budget_types():
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    is_revenue = request.args.get('is_revenue', default=False, type=bool)
    entities = budget_type_repository.all_by_condition(is_revenue=is_revenue, page_sort_params=page_sort_params)
    result = BudgetTypeModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/budget/recapitulations/year/<string:year>', methods=['GET'])
@cache.cached(timeout=1800, query_string=True)
def get_budget_recapitulations_by_year(year):
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)

    is_lokpri = request.args.get('is_lokpri', default=True, type=bool)
    region_id = request.args.get('region_id', default=None, type=str)
    entities = None
    if region_id is None:
        entities = budget_recapitulation_repository.all_by_year(year, is_lokpri, page_sort_params)
    else:
        entities = budget_recapitulation_repository.get_by_region_and_year(region_id, year, page_sort_params)

    is_full_region = request.args.get('is_full_region', default=True, type=bool)
    if is_full_region:
        result = BudgetRecapitulationCompleteModelSchema(many=True).dump(entities)
    else:
        result = BudgetRecapitulationModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/budget/recapitulations/year/<string:year>/count', methods=['GET'])
@cache.cached(timeout=1800, query_string=True)
def get_budget_recapitulations_count_by_year(year):
    is_lokpri = request.args.get('is_lokpri', default=True, type=bool)
    result = budget_recapitulation_repository.count_by_year(year, is_lokpri)
    return jsonify(result)


@app.route('/budget/recapitulations/region/<string:region_id>/year/<string:year>', methods=['GET'])
@cache.cached(timeout=1800, query_string=True)
def get_budget_recapitulations_by_region_and_year(region_id, year):
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = budget_recapitulation_repository.get_by_region_and_year(region_id, year, page_sort_params)
    result = BudgetRecapitulationModelSchema(many=True).dump(entities)
    return jsonify(result.data)
