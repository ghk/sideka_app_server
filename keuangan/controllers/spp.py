from flask import Blueprint, jsonify, request
from datetime import datetime
from keuangan import db
from keuangan.models import SiskeudesSppModelSchema, SiskeudesSppBuktiModelSchema, SiskeudesSppRinciModelSchema
from keuangan.repository import RegionRepository, SidekaContentRepository
from keuangan.repository import SiskeudesSppRepository, SiskeudesSppBuktiRepository, SiskeudesSppRinciRepository
from keuangan.helpers import QueryHelper, ContentTransformer

app = Blueprint('spp', __name__)
region_repository = RegionRepository(db)
sideka_content_repository = SidekaContentRepository(db)
siskeudes_spp_repository = SiskeudesSppRepository(db)
siskeudes_spp_bukti_repository = SiskeudesSppBuktiRepository(db)
siskeudes_spp_rinci_repository = SiskeudesSppRinciRepository(db)


@app.route('/siskeudes/spps', methods=['GET'])
def get_siskeudes_spps():
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = siskeudes_spp_repository.all(page_sort_params)
    result = SiskeudesSppModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/spps/count', methods=['GET'])
def get_siskeudes_spps_count():
    result = siskeudes_spp_repository.count()
    return jsonify(result)


@app.route('/siskeudes/spps/region/<string:region_id>', methods=['GET'])
def get_siskeudes_spps_by_region(region_id):
    entities = siskeudes_spp_repository.get_by_region(region_id)
    result = SiskeudesSppModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/spps/buktis', methods=['GET'])
def get_siskeudes_spps_buktis():
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = siskeudes_spp_bukti_repository.all(page_sort_params)
    result = SiskeudesSppBuktiModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/spps/buktis/count', methods=['GET'])
def get_siskeudes_spps_buktis_count():
    result = siskeudes_spp_bukti_repository.count()
    return jsonify(result)


@app.route('/siskeudes/spps/buktis/region/<string:region_id>', methods=['GET'])
def get_siskeudes_spps_buktis_by_region(region_id):
    entities = siskeudes_spp_bukti_repository.get_by_region(region_id)
    result = SiskeudesSppBuktiModelSchema(many=True).dump(entities)
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
    # delete all spp, spp bukti and spp rinci
    siskeudes_spp_repository.delete_all()
    siskeudes_spp_bukti_repository.delete_all()
    siskeudes_spp_rinci_repository.delete_all()

    year = str(datetime.now().year)
    regions = region_repository.all()
    sd_contents = sideka_content_repository.get_latest_content('spp', year)

    for sd_content in sd_contents:
        contents = ContentTransformer.transform(sd_content.content)
        for region in regions:
            spps = SiskeudesSppModelSchema(many=True).load(contents['spp'])
            sppbs = SiskeudesSppBuktiModelSchema(many=True).load(contents['spp_bukti'])
            spprs = SiskeudesSppRinciModelSchema(many=True).load(contents['spp_rinci'])
            siskeudes_spp_repository.add_all(spps.data, region, year)
            siskeudes_spp_bukti_repository.add_all(sppbs.data, region, year)
            siskeudes_spp_rinci_repository.add_all(spprs.data, region, year)

    return jsonify({'success': True})
