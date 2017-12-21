from flask import Blueprint, jsonify, request
from keuangan import db
from keuangan.models import BudgetLikelihoodModelSchema
from keuangan.repository import BudgetLikelihoodRepository
from keuangan.helpers import QueryHelper

app = Blueprint('likelihood', __name__)
budget_likelihood_repository = BudgetLikelihoodRepository(db)


@app.route('/budget/likelihoods/year/<string:year>', methods=['GET'])
def get_budget_likelihoods_by_year(year):
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    is_lokpri = request.args.get('is_lokpri', default=True, type=bool)
    entities = budget_likelihood_repository.all_by_year(year, is_lokpri, page_sort_params)
    result = BudgetLikelihoodModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/budget/likelihoods/year/<string:year>/count', methods=['GET'])
def get_budget_likelihoods_count_by_year(year):
    is_lokpri = request.args.get('is_lokpri', default=True, type=bool)
    result = budget_likelihood_repository.count_by_year(year, is_lokpri)
    return jsonify(result)


@app.route('/budget/likelihoods/region/<string:region_id>/year/<string:year>', methods=['GET'])
def get_budget_likelihoods_by_region_and_year(region_id, year):
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = budget_likelihood_repository.get_by_region_and_year(region_id, year, page_sort_params)
    result = BudgetLikelihoodModelSchema(many=True).dump(entities)
    return jsonify(result.data)
