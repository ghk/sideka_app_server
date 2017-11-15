from flask import Blueprint, jsonify, request
from keuangan import db
from keuangan.models import SiskeudesKegiatanModelSchema
from keuangan.repository import SiskeudesKegiatanRepository
from keuangan.helpers import QueryHelper

app = Blueprint('kegiatan', __name__)
siskeudes_kegiatan_repository = SiskeudesKegiatanRepository(db)


@app.route('/siskeudes/kegiatans/', methods=['GET'])
def get_siskeudes_kegiatans():
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = siskeudes_kegiatan_repository.all(page_sort_params=page_sort_params)
    result = SiskeudesKegiatanModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/kegiatans/count', methods=['GET'])
def get_siskeudes_kegiatans_count():
    result = siskeudes_kegiatan_repository.count()
    return jsonify(result)


@app.route('/siskeudes/kegiatans/region/<string:region_id>', methods=['GET'])
def get_siskeudes_kegiatans_by_region(region_id):
    entities = siskeudes_kegiatan_repository.get_by_region(region_id)
    result = SiskeudesKegiatanModelSchema(many=True).dump(entities)
    return jsonify(result.data)
