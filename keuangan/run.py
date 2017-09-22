import os, requests, urlparse, simplejson as json
from flask import jsonify, request

from keuangan import app, db
from keuangan.models import *
from keuangan.helpers import *

BASE_URL = os.path.abspath(os.path.dirname(__file__))
CLIENT_FOLDER = os.path.join(BASE_URL, "client")
API_URL = app.config['API_URL']


@app.route('/regions', methods=['GET'])
def get_regions():
    regions = db.session.query(Region).filter(Region.is_lokpri == True).all()
    result = RegionSchema(many=True).dump(regions)
    return jsonify(result.data)


@app.route('/regions/count', methods=['GET'])
def get_regions_count():
    result = db.session.query(Region).filter(Region.is_lokpri == True).count()
    return jsonify(result)


@app.route('/regions/<string:id>', methods=['GET'])
def get_region(id):
    region = db.session.query(Region).filter(Region.id == id and Region.is_lokpri == True).first()
    result = RegionSchema(many=False).dump(region)
    return jsonify(result.data)


@app.route('/progress/recapitulations', methods=['GET'])
def get_progress_recapitulations():
    query = db.session.query(ProgressRecapitulation)
    query = QueryHelper.build_sort_query(query, ProgressRecapitulation, request)
    query = QueryHelper.build_page_query(query, request)
    prs = query.all()
    result = ProgressRecapitulationSchema(many=True).dump(prs)
    return jsonify(result.data)


@app.route('/progress/recapitulations/count', methods=['GET'])
def get_progress_recapitulations_count():
    result = db.session.query(ProgressRecapitulation).count()
    return jsonify(result)


@app.route('/progress/recapitulations/generate', methods=['GET'])
def generate_progress_recapitulations():
    regions = db.session.query(Region).filter(Region.is_lokpri == True).all()

    for region in regions:
        pr = Generator.generate_progress_recapitulation()
        pr.fk_region_id = region.id
        db.session.add(pr)

    db.session.commit()


@app.route('/progress/timelines', methods=['GET'])
def get_progress_timelines():
    query = db.session.query(ProgressTimeline)
    query = QueryHelper.build_sort_query(query, ProgressTimeline, request)
    query = QueryHelper.build_page_query(query, request)
    pts = query.all()
    result = ProgressTimelineSchema(many=True).dump(pts)
    return jsonify(result.data)


@app.route('/progress/timelines/count', methods=['GET'])
def get_progress_timelines_count():
    result = db.session.query(ProgressTimeline).count()
    return jsonify(result)


@app.route('/progress/timelines/region/<string:region_id>', methods=['GET'])
def get_region_progress_timelines(region_id):
    query = db.session.query(ProgressTimeline) \
        .filter(ProgressTimeline.fk_region_id == region_id)
    pts = query.all()
    result = ProgressTimelineSchema(many=True).dump(pts)
    return jsonify(result.data)


@app.route('/progress/timelines/generate', methods=['GET'])
def generate_progress_timelines():
    regions = db.session.query(Region).filter(Region.is_lokpri == True).all()
    months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    for region in regions:
        for month in months:
            pt = Generator.generate_progress_timeline()
            pt.month = month
            pt.fk_region_id = region.id
            db.session.add(pt)
    db.session.commit()


@app.route('/spending/types', methods=['GET'])
def get_spending_types():
    query = db.session.query(SpendingType)
    query = QueryHelper.build_sort_query(query, SpendingType, request)
    query = QueryHelper.build_page_query(query, request)
    spending_types = query.all()
    result = SpendingTypeSchema(many=True).dump(spending_types)
    return jsonify(result.data)


@app.route('/spending/types/generate', methods=['GET'])
def generate_spending_types():
    spending_types = ['Pendapatan', 'Infrastruktur', 'Ekonomi dan Pembinaan Masyarakat',
                      'Pendidikan dan Pelatihan', 'Belanja Pegawai', 'Pemerintahan Umum',
                      'Pembangunan Kantor Desa']
    for spending_type in spending_types:
        st = SpendingType()
        st.name = spending_type
        db.session.add(st)
    db.session.commit()


@app.route('/spending/recapitulations', methods=['GET'])
def get_spending_recapitulations():
    query = db.session.query(SpendingRecapitulation)
    query = QueryHelper.build_sort_query(query, SpendingRecapitulation, request)
    query = QueryHelper.build_page_query(query, request)
    srs = query.all()
    result = SpendingRecapitulationSchema(many=True).dump(srs)
    return jsonify(result.data)


@app.route('/spending/recapitulations/count', methods=['GET'])
def get_spending_recapitulations_count():
    result = db.session.query(SpendingRecapitulation).count()
    return jsonify(result)


@app.route('/spending/recapitulations/generate', methods=['GET'])
def generate_spending_recapitulations():
    regions = db.session.query(Region).filter(Region.is_lokpri == True).all()
    spending_types = db.session.query(SpendingType).all()
    for region in regions:
        for spending_type in spending_types:
            sr = Generator.generate_spending_recapitulations()
            sr.fk_region_id = region.id
            sr.fk_type_id = spending_type.id
            db.session.add(sr)
    db.session.commit()


@app.route('/siskeudes/kegiatans/', methods=['GET'])
def get_siskeudes_kegiatans():
    sks = db.session.query(SiskeudesKegiatan).all()
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
    desas = requests.get(urlparse.urljoin(API_URL, 'desa')).json()
    regions = db.session.query(Region).filter(Region.is_lokpri == True).all()

    for region in regions:
        for desa in desas:
            if (str(region.id).strip() == str(desa.kode).strip()):
                #sps = requests.get(urlparse.urljoin(API_URL, 'content/v2/', ), )


@app.route('/siskeudes/penganggarans', methods=['GET'])
def get_siskeudes_rabs():
    query = db.session.query(SiskeudesPenganggaran)
    query = QueryHelper.build_sort_query(query, SiskeudesPenganggaran, request)
    query = QueryHelper.build_page_query(query, request)
    srs = query.all()
    result = SpendingRecapitulationSchema(many=True).dump(srs)
    return jsonify(result.data)


@app.route('/siskeudes/penganggarans/count', methods=['GET'])
def get_spending_budgets_count():
    result = db.session.query(SiskeudesPenganggaran).count()
    return jsonify(result)


@app.route('/siskeudes/penganggarans/region/<string:region_id>', methods=['GET'])
def get_spending_budgets_by_region(region_id):
    sbs = db.session.query(SiskeudesPenganggaran) \
        .filter(SiskeudesPenganggaran.fk_region_id == region_id) \
        .all()
    result = SiskeudesPenganggaranSchema(many=True).dump(sbs)
    return jsonify(result.data)


@app.route('/siskeudes/spp', methods=['GET'])
def get_progress_spendings():
    realizations = db.session.query(SiskeudesSpp).all()
    result = SiskeudesSppSchema(many=True).dump(realizations)
    return jsonify(result.data)


@app.route('/siskeudes/spp/count', methods=['GET'])
def get_progress_spendings_count():
    result = db.session.query(SiskeudesSpp).count()
    return jsonify(result)


@app.route('/siskeudes/spp/region/<string:region_id>', methods=['GET'])
def get_progress_spendings_by_region(region_id):
    realizations = db.session.query(SiskeudesSpp) \
        .filter(SiskeudesSpp.fk_region_id == region_id) \
        .all()
    result = SiskeudesSppSchema(many=True).dump(realizations)
    return jsonify(result.data)


@app.route('/siskeudes/spp/bukti', methods=['GET'])
def get_progress_spendings():
    realizations = db.session.query(SiskeudesSppBukti).all()
    result = SiskeudesSppBuktiSchema(many=True).dump(realizations)
    return jsonify(result.data)


@app.route('/siskeudes/spp/bukti/count', methods=['GET'])
def get_progress_spendings_count():
    result = db.session.query(SiskeudesSppBukti).count()
    return jsonify(result)


@app.route('/siskeudes/spp/bukti/region/<string:region_id>', methods=['GET'])
def get_progress_spendings_by_region(region_id):
    realizations = db.session.query(SiskeudesSppBukti) \
        .filter(SiskeudesSppBukti.fk_region_id == region_id) \
        .all()
    result = SiskeudesSppBuktiSchema(many=True).dump(realizations)
    return jsonify(result.data)


@app.route('/siskeudes/spp/rinci', methods=['GET'])
def get_progress_spendings():
    realizations = db.session.query(SiskeudesSppRinci).all()
    result = SiskeudesSppRinciSchema(many=True).dump(realizations)
    return jsonify(result.data)


@app.route('/siskeudes/spp/rinci/count', methods=['GET'])
def get_progress_spendings_count():
    result = db.session.query(SiskeudesSppRinci).count()
    return jsonify(result)


@app.route('/siskeudes/spp/rinci/region/<string:region_id>', methods=['GET'])
def get_progress_spendings_by_region(region_id):
    realizations = db.session.query(SiskeudesSppRinci) \
        .filter(SiskeudesSppRinci.fk_region_id == region_id) \
        .all()
    result = SiskeudesSppRinciSchema(many=True).dump(realizations)
    return jsonify(result.data)


@app.route('/generate', methods=['GET'])
def generate_all():
    generate_progress_recapitulations()
    generate_progress_timelines()
    generate_spending_types()
    generate_spending_recapitulations()


if __name__ == "__main__":
    db.create_all();
    app.run(debug=True, host=app.config["HOST"], port=app.config["KEUANGAN_PORT"])
