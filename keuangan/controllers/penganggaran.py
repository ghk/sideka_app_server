from flask import Blueprint, jsonify, request
from keuangan import db
from keuangan.models import SiskeudesPenganggaranModelSchema, SiskeudesPenganggaranSchema
from keuangan.repository import RegionRepository, SidekaContentRepository
from keuangan.repository import SiskeudesPenganggaranRepository, SiskeudesKegiatanRepository
from keuangan.helpers import QueryHelper, SiskeudesFetcher

app = Blueprint('penganggaran', __name__)
region_repository = RegionRepository(db)
sideka_content_repository = SidekaContentRepository(db)
siskeudes_penganggaran_repository = SiskeudesPenganggaranRepository(db)
siskeudes_kegiatan_repository = SiskeudesKegiatanRepository(db)


@app.route('/siskeudes/penganggarans', methods=['GET'])
def get_siskeudes_penganggarans():
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = siskeudes_penganggaran_repository.all(page_sort_params)
    result = SiskeudesPenganggaranModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/penganggarans/count', methods=['GET'])
def get_siskeudes_penganggarans_count():
    result = siskeudes_penganggaran_repository.count()
    return jsonify(result)


@app.route('/siskeudes/penganggarans/region/<string:region_id>', methods=['GET'])
def get_siskeudes_penganggarans_by_region(region_id):
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = siskeudes_penganggaran_repository.get_by_region(region_id)
    result = SiskeudesPenganggaranModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/penganggarans/fetch', methods=['GET'])
def fetch_siskeudes_penganggarans():
    SiskeudesFetcher.fetch_penganggarans()
    db.session.commit()
    return jsonify({'success': True})

