from flask import Blueprint, jsonify, request
from keuangan import db
from keuangan.models import SiskeudesPenganggaranModelSchema, SiskeudesPenganggaranSchema
from keuangan.repository import RegionRepository, SiskeudesPenganggaranRepository, SiskeudesKegiatanRepository
from keuangan.helpers import QueryHelper, SiskeudesFetcher

app = Blueprint('penganggaran', __name__)
region_repository = RegionRepository(db)
siskeudes_penganggaran_repository = SiskeudesPenganggaranRepository(db)


@app.route('/siskeudes/penganggarans/year/<string:year>', methods=['GET'])
def get_siskeudes_penganggarans_by_year(year):
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = siskeudes_penganggaran_repository.all_by_year(year, page_sort_params)
    result = SiskeudesPenganggaranModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/penganggarans/year/<string:year>/count', methods=['GET'])
def get_siskeudes_penganggarans_count_by_year(year):
    result = siskeudes_penganggaran_repository.count_by_year(year)
    return jsonify(result)


@app.route('/siskeudes/penganggarans/region/<string:region_id>/year/<string:year>', methods=['GET'])
def get_siskeudes_penganggarans_by_region_and_year(region_id, year):
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = siskeudes_penganggaran_repository.get_by_region_and_year(region_id, year, page_sort_params)
    result = SiskeudesPenganggaranModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/penganggarans/region/<string:region_id>/year/<string:year>/spending', methods=['GET'])
def get_siskeudes_penganggarans_total_spending_by_region_and_year(region_id, year):
    result = siskeudes_penganggaran_repository.get_total_spending_by_region_and_year(region_id, year)
    return jsonify(result)


@app.route('/siskeudes/penganggarans/fetch', methods=['GET'])
def fetch_siskeudes_penganggarans():
    SiskeudesFetcher.fetch_penganggarans()
    db.session.commit()
    return jsonify({'success': True})


@app.route('/siskeudes/penganggarans/fetch/region/<string:region_id>', methods=['GET'])
def fetch_siskeudes_penganggarans_by_region(region_id):
    region = region_repository.get(region_id)
    SiskeudesFetcher.fetch_penganggaran_by_region(region)
    db.session.commit()
    return jsonify({'success': True})
