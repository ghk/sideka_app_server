from flask import Blueprint, jsonify, request
from datetime import datetime
from keuangan import db
from keuangan.models import SiskeudesPenerimaanModelSchema, SiskeudesPenerimaanRinciModelSchema
from keuangan.repository import RegionRepository, SidekaContentRepository
from keuangan.repository import SiskeudesPenerimaanRepository, SiskeudesPenerimaanRinciRepository
from keuangan.helpers import QueryHelper, ContentTransformer

app = Blueprint('penerimaan', __name__)
region_repository = RegionRepository(db)
sideka_content_repository = SidekaContentRepository(db)
siskeudes_penerimaan_repository = SiskeudesPenerimaanRepository(db)
siskeudes_penerimaan_rinci_repository = SiskeudesPenerimaanRinciRepository(db)


@app.route('/siskeudes/penerimaans', methods=['GET'])
def get_siskeudes_penerimaans():
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = siskeudes_penerimaan_repository.all(page_sort_params)
    result = SiskeudesPenerimaanModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/penerimaans/count', methods=['GET'])
def get_siskeudes_penerimaans_count():
    result = siskeudes_penerimaan_repository.count()
    return jsonify(result)


@app.route('/siskeudes/penerimaans/region/<string:region_id>', methods=['GET'])
def get_siskeudes_penerimaans_by_region(region_id):
    entities = siskeudes_penerimaan_repository.get_by_region(region_id)
    result = SiskeudesPenerimaanModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/penerimaans/fetch', methods=['GET'])
def fetch_siskeudes_penerimaans():
    year = str(datetime.now().year)
    regions = region_repository.all()

    for region in regions:
        # delete all penerimaan and penerimaan rincis
        siskeudes_penerimaan_repository.delete_by_region(region.id)
        siskeudes_penerimaan_rinci_repository.delete_by_region(region.id)

        sd_content = sideka_content_repository.get_latest_content_by_desa_id('penerimaan', year, region.desa_id)
        contents = ContentTransformer.transform(sd_content.content)

        sps = SiskeudesPenerimaanModelSchema(many=True).load(contents['tbp'])
        sprs = SiskeudesPenerimaanRinciModelSchema(many=True).load(contents['tbp_rinci'])
        siskeudes_penerimaan_repository.add_all(sps.data, region, year)
        siskeudes_penerimaan_rinci_repository.add_all(sprs.data, region, year)

    return jsonify({'success': True})


@app.route('/siskeudes/penerimaans/rincis', methods=['GET'])
def get_siskeudes_penerimaan_rincis():
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = siskeudes_penerimaan_rinci_repository.all(page_sort_params)
    result = SiskeudesPenerimaanRinciModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/penerimaans/rincis/count', methods=['GET'])
def get_siskeudes_penerimaan_rincis_count():
    result = siskeudes_penerimaan_rinci_repository.count()
    return jsonify(result)


@app.route('/siskeudes/penerimaans/rincis/region/<string:region_id>', methods=['GET'])
def get_siskeudes_penerimaan_rincis_by_region(region_id):
    entities = siskeudes_penerimaan_rinci_repository.get_by_region(region_id)
    result = SiskeudesPenerimaanRinciModelSchema(many=True).dump(entities)
    return jsonify(result.data)
