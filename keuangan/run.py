import os
from flask import jsonify, request
from sqlalchemy import func, and_

from keuangan import create_app, db
from keuangan.models import *
from keuangan.helpers import *

app = create_app()
BASE_URL = os.path.abspath(os.path.dirname(__file__))
CLIENT_FOLDER = os.path.join(BASE_URL, "client")
API_URL = app.config['API_URL']


@app.route('/siskeudes/penerimaans', methods=['GET'])
def get_siskeudes_penerimaans():
    revenues = db.session.query(SiskeudesPenerimaan).all()
    result = SiskeudesPenerimaanSchema(many=True).dump(revenues)
    return jsonify(result.data)


@app.route('/siskeudes/penerimaans/count', methods=['GET'])
def get_siskeudes_penerimaans_count():
    result = db.session.query(SiskeudesPenerimaan).count()
    return jsonify(result)


@app.route('/siskeudes/penerimaans/region/<string:region_id>', methods=['GET'])
def get_siskeudes_penerimaans_by_region(region_id):
    revenues = db.session.query(SiskeudesPenerimaan) \
        .filter(SiskeudesPenerimaan.fk_region_id == region_id) \
        .all()
    result = SiskeudesPenerimaanSchema(many=True).dump(revenues)
    return jsonify(result.data)


@app.route('/siskeudes/penerimaans/fetch', methods=['GET'])
def fetch_siskeudes_penerimaans():
    regions = db.session.query(Region).filter(Region.is_lokpri == True).all()

    subq = db.session.query(SdContent, func.max(SdContent.change_id).label('max_change_id'))\
        .filter(SdContent.type == 'penerimaan')\
        .filter(SdContent.subtype == '2017')\
        .group_by(SdContent.desa_id)\
        .subquery()

    sds = db.session.query(SdContent)\
        .join(subq, and_(
            SdContent.desa_id == subq.c.desa_id,
            SdContent.type == subq.c.type,
            SdContent.subtype == subq.c.subtype,
            SdContent.change_id == subq.c.max_change_id
        ))\
        .all()

    for sd in sds:
        contents = ContentTransformer.transform(sd.content)

        for region in regions:
            sps = SiskeudesPenerimaanSchema(many=True).load(contents['tbp'])
            sprs = SiskeudesPenerimaanRinciSchema(many=True).load(contents['tbp_rinci'])
            for sp in sps.data:
                sp.year = '2017'
                sp.fk_region_id = region.id
                db.session.add(sp)
            for spr in sprs.data:
                spr.year = '2017'
                spr.fk_region_id = region.id
                db.session.add(spr)

    db.session.commit()
    result = SdContentSchema(many=True).dump(sds)
    return jsonify(result.data)


@app.route('/siskeudes/penganggarans', methods=['GET'])
def get_siskeudes_penganggarans():
    query = db.session.query(SiskeudesPenganggaran)
    query = QueryHelper.build_sort_query(query, SiskeudesPenganggaran, request)
    query = QueryHelper.build_page_query(query, request)
    srs = query.all()
    result = SpendingRecapitulationSchema(many=True).dump(srs)
    return jsonify(result.data)


@app.route('/siskeudes/penganggarans/count', methods=['GET'])
def get_siskeudes_penganggarans_count():
    result = db.session.query(SiskeudesPenganggaran).count()
    return jsonify(result)


@app.route('/siskeudes/penganggarans/region/<string:region_id>', methods=['GET'])
def get_siskeudes_penganggarans_by_region(region_id):
    sbs = db.session.query(SiskeudesPenganggaran) \
        .filter(SiskeudesPenganggaran.fk_region_id == region_id) \
        .all()
    result = SiskeudesPenganggaranSchema(many=True).dump(sbs)
    return jsonify(result.data)


@app.route('/siskeudes/spps', methods=['GET'])
def get_siskeudes_spps():
    realizations = db.session.query(SiskeudesSpp).all()
    result = SiskeudesSppSchema(many=True).dump(realizations)
    return jsonify(result.data)


@app.route('/siskeudes/spps/count', methods=['GET'])
def get_siskeudes_spps_count():
    result = db.session.query(SiskeudesSpp).count()
    return jsonify(result)


@app.route('/siskeudes/spps/region/<string:region_id>', methods=['GET'])
def get_siskeudes_spps_by_region(region_id):
    realizations = db.session.query(SiskeudesSpp) \
        .filter(SiskeudesSpp.fk_region_id == region_id) \
        .all()
    result = SiskeudesSppSchema(many=True).dump(realizations)
    return jsonify(result.data)


@app.route('/siskeudes/spps/buktis', methods=['GET'])
def get_siskeudes_spps_buktis():
    realizations = db.session.query(SiskeudesSppBukti).all()
    result = SiskeudesSppBuktiSchema(many=True).dump(realizations)
    return jsonify(result.data)


@app.route('/siskeudes/spps/buktis/count', methods=['GET'])
def get_siskeudes_spps_buktis_count():
    result = db.session.query(SiskeudesSppBukti).count()
    return jsonify(result)


@app.route('/siskeudes/spps/buktis/region/<string:region_id>', methods=['GET'])
def get_siskeudes_spps_buktis_by_region(region_id):
    realizations = db.session.query(SiskeudesSppBukti) \
        .filter(SiskeudesSppBukti.fk_region_id == region_id) \
        .all()
    result = SiskeudesSppBuktiSchema(many=True).dump(realizations)
    return jsonify(result.data)


@app.route('/siskeudes/spps/rincis', methods=['GET'])
def get_siskeudes_spps_rincis():
    realizations = db.session.query(SiskeudesSppRinci).all()
    result = SiskeudesSppRinciSchema(many=True).dump(realizations)
    return jsonify(result.data)


@app.route('/siskeudes/spps/rincis/count', methods=['GET'])
def get_siskeudes_spps_rincis_count():
    result = db.session.query(SiskeudesSppRinci).count()
    return jsonify(result)


@app.route('/siskeudes/spps/rincis/region/<string:region_id>', methods=['GET'])
def get_siskeudes_spps_rincis_by_region(region_id):
    realizations = db.session.query(SiskeudesSppRinci) \
        .filter(SiskeudesSppRinci.fk_region_id == region_id) \
        .all()
    result = SiskeudesSppRinciSchema(many=True).dump(realizations)
    return jsonify(result.data)


if __name__ == "__main__":
    app.run(debug=True, host=app.config["HOST"], port=app.config["KEUANGAN_PORT"])
