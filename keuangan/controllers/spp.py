from flask import Blueprint, jsonify, request
from keuangan import db
from keuangan.models import SiskeudesSppModelSchema, SiskeudesSppBuktiModelSchema, SiskeudesSppRinciModelSchema
from keuangan.models import SiskeudesSppModelSchemaIso, SiskeudesSppBuktiModelSchemaIso
from keuangan.repository import SiskeudesSppRepository, SiskeudesSppBuktiRepository, SiskeudesSppRinciRepository
from keuangan.helpers import QueryHelper, SiskeudesFetcher

app = Blueprint('spp', __name__)
siskeudes_spp_repository = SiskeudesSppRepository(db)
siskeudes_spp_bukti_repository = SiskeudesSppBuktiRepository(db)
siskeudes_spp_rinci_repository = SiskeudesSppRinciRepository(db)


@app.route('/siskeudes/spps', methods=['GET'])
def get_siskeudes_spps():
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = siskeudes_spp_repository.all(page_sort_params)
    result = SiskeudesSppModelSchemaIso(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/spps/count', methods=['GET'])
def get_siskeudes_spps_count():
    result = siskeudes_spp_repository.count()
    return jsonify(result)


@app.route('/siskeudes/spps/region/<string:region_id>', methods=['GET'])
def get_siskeudes_spps_by_region(region_id):
    entities = siskeudes_spp_repository.get_by_region(region_id)
    result = SiskeudesSppModelSchemaIso(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/spps/buktis', methods=['GET'])
def get_siskeudes_spps_buktis():
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = siskeudes_spp_bukti_repository.all(page_sort_params)
    result = SiskeudesSppBuktiModelSchemaIso(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/spps/buktis/count', methods=['GET'])
def get_siskeudes_spps_buktis_count():
    result = siskeudes_spp_bukti_repository.count()
    return jsonify(result)


@app.route('/siskeudes/spps/buktis/region/<string:region_id>', methods=['GET'])
def get_siskeudes_spps_buktis_by_region(region_id):
    entities = siskeudes_spp_bukti_repository.get_by_region(region_id)
    result = SiskeudesSppBuktiModelSchemaIso(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/spps/rincis', methods=['GET'])
def get_siskeudes_spps_rincis():
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = siskeudes_spp_rinci_repository.all(page_sort_params)
    result = SiskeudesSppRinciModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/spps/rincis/count', methods=['GET'])
def get_siskeudes_spps_rincis_count():
    result = siskeudes_spp_rinci_repository.count()
    return jsonify(result)


@app.route('/siskeudes/spps/rincis/region/<string:region_id>', methods=['GET'])
def get_siskeudes_spps_rincis_by_region(region_id):
    entities = siskeudes_spp_rinci_repository.get_by_region(region_id)
    result = SiskeudesSppRinciModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/spps/fetch', methods=['GET'])
def fetch_siskeudes_spps():
    SiskeudesFetcher.fetch_spps()
    db.session.commit()
    return jsonify({'success': True})
