from flask import Blueprint, jsonify
from keuangan import db
from keuangan.models import SiskeudesKegiatan, SiskeudesKegiatanSchema
from keuangan.repository import SiskeudesKegiatanRepository

app = Blueprint('kegiatan', __name__)
sk_repository = SiskeudesKegiatanRepository(db)


@app.route('/siskeudes/kegiatans/', methods=['GET'])
def get_siskeudes_kegiatans():
    page_sort_params = get
    entities = sk_repository.all()
    result = SiskeudesKegiatanSchema(many=True).dump(sks)
    return jsonify(result.data)


@app.route('/siskeudes/kegiatans/count', methods=['GET'])
def get_siskeudes_kegiatans_count():
    result = db.session.query(SiskeudesKegiatan).count()
    return jsonify(result)


@app.route('/siskeudes/kegiatans/region/<string:region_id>', methods=['GET'])
def get_siskeudes_kegiatans_by_region(region_id):
    sks = db.session.query(SiskeudesKegiatan)\
        .filter(SiskeudesKegiatan.fk_region_id == region_id)\
        .all()
    result = SiskeudesKegiatanSchema(many=True).dump(sks)
    return jsonify(result.data)