import os, sys
from flask import jsonify, request

from keuangan import app, db
from keuangan.models import *
from keuangan.helpers import *

print sys.path

BASE_URL = os.path.abspath(os.path.dirname(__file__))
CLIENT_FOLDER = os.path.join(BASE_URL, "client")


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


@app.route('/progress_recapitulations', methods=['GET'])
def get_progress_recapitulations():
    query = db.session.query(ProgressRecapitulation)
    query = QueryHelper.build_sort_query(query, ProgressRecapitulation, request)
    query = QueryHelper.build_page_query(query, request)
    prs = query.all()
    result = ProgressRecapitulationSchema(many=True).dump(prs)
    return jsonify(result.data)


@app.route('/progress_recapitulations/count', methods=['GET'])
def get_progress_recapitulations_count():
    result = db.session.query(ProgressRecapitulation).count()
    return jsonify(result)


@app.route('/progress_recapitulations/generate', methods=['GET'])
def generate_progress_recapitulations():
    regions = db.session.query(Region).filter(Region.is_lokpri == True).all()

    for region in regions:
        pr = Generator.generate_progress_recapitulation()
        pr.fk_region_id = region.id
        db.session.add(pr)

    db.session.commit()


@app.route('/progress_timelines', methods=['GET'])
def get_progress_timelines():
    query = db.session.query(ProgressTimeline)
    query = QueryHelper.build_sort_query(query, ProgressTimeline, request)
    query = QueryHelper.build_page_query(query, request)
    pts = query.all()
    result = ProgressTimelineSchema(many=True).dump(pts)
    return jsonify(result.data)


@app.route('/progress_timelines/count', methods=['GET'])
def get_progress_timelines_count():
    result = db.session.query(ProgressTimeline).count()
    return jsonify(result)


@app.route('/progress_timelines/region/<string:region_id>', methods=['GET'])
def get_region_progress_timelines(region_id):
    query = db.session.query(ProgressTimeline) \
        .filter(ProgressTimeline.fk_region_id == region_id)
    pts = query.all()
    result = ProgressTimelineSchema(many=True).dump(pts)
    return jsonify(result.data)


@app.route('/progress_timelines/generate', methods=['GET'])
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


@app.route('/progress_revenues', methods=['GET'])
def get_progress_revenues():
    revenues = db.session.query(ProgressRevenue).all()
    result = ProgressRevenueSchema(many=True).dump(revenues)
    return jsonify(result.data)


@app.route('/progress_revenues/count', methods=['GET'])
def get_progress_revenues_count():
    result = db.session.query(ProgressRevenue).count()
    return jsonify(result)


@app.route('/progress_revenues/region/<string:region_id>', methods=['GET'])
def get_progress_revenues_by_region(region_id):
    revenues = db.session.query(ProgressRevenue) \
        .filter(ProgressRevenue.fk_region_id == region_id) \
        .all()
    result = ProgressRevenueSchema(many=True).dump(revenues)
    return jsonify(result.data)


@app.route('/progress_revenues/generate', methods=['GET'])
def generate_progress_revenues():
    regions = db.session.query(Region).filter(Region.is_lokpri == True).all()
    for region in regions:
        pr = Generator.generate_progress_revenue()
        pr.fk_region_id = region.id
        db.session.add(pr)
    db.session.commit()


@app.route('/progress_spendings', methods=['GET'])
def get_progress_spendings():
    realizations = db.session.query(ProgressSpending).all()
    result = ProgressSpendingSchema(many=True).dump(realizations)
    return jsonify(result.data)


@app.route('/progress_spendings/count', methods=['GET'])
def get_progress_spendings_count():
    result = db.session.query(ProgressSpending).count()
    return jsonify(result)


@app.route('/progress_spendings/region/<string:region_id>', methods=['GET'])
def get_progress_spendings_by_region(region_id):
    realizations = db.session.query(ProgressSpending) \
        .filter(ProgressSpending.fk_region_id == region_id) \
        .all()
    result = ProgressSpendingSchema(many=True).dump(realizations)
    return jsonify(result.data)


@app.route('/progress_realizations/generate', methods=['GET'])
def generate_progress_spendings():
    regions = db.session.query(Region).filter(Region.is_lokpri == True).all()
    for region in regions:
        pr = Generator.generate_progress_realization()
        pr.fk_region_id = region.id
        db.session.add(pr)
    db.session.commit()


@app.route('/spending_types', methods=['GET'])
def get_spending_types():
    query = db.session.query(SpendingType)
    query = QueryHelper.build_sort_query(query, SpendingType, request)
    query = QueryHelper.build_page_query(query, request)
    spending_types = query.all()
    result = SpendingTypeSchema(many=True).dump(spending_types)
    return jsonify(result.data)


@app.route('/spending_types/generate', methods=['GET'])
def generate_spending_types():
    spending_types = ['Pendapatan', 'Infrastruktur', 'Ekonomi dan Pembinaan Masyarakat',
                      'Pendidikan dan Pelatihan', 'Belanja Pegawai', 'Pemerintahan Umum',
                      'Pembangunan Kantor Desa']
    for spending_type in spending_types:
        st = SpendingType()
        st.name = spending_type
        db.session.add(st)
    db.session.commit()


@app.route('/spending_recapitulations', methods=['GET'])
def get_spending_recapitulations():
    query = db.session.query(SpendingRecapitulation)
    query = QueryHelper.build_sort_query(query, SpendingRecapitulation, request)
    query = QueryHelper.build_page_query(query, request)
    srs = query.all()
    result = SpendingRecapitulationSchema(many=True).dump(srs)
    return jsonify(result.data)


@app.route('/spending_recapitulations/count', methods=['GET'])
def get_spending_recapitulations_count():
    result = db.session.query(SpendingRecapitulation).count()
    return jsonify(result)


@app.route('/spending_recapitulations/generate', methods=['GET'])
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


@app.route('/siskeudes/rab', methods=['GET'])
def get_siskeudes_rabs():
    query = db.session.query(SiskeudesRab)
    query = QueryHelper.build_sort_query(query, SiskeudesRab, request)
    query = QueryHelper.build_page_query(query, request)
    srs = query.all()
    result = SpendingRecapitulationSchema(many=True).dump(srs)
    return jsonify(result.data)


@app.route('/siskeudes/rab/count', methods=['GET'])
def get_spending_budgets_count():
    result = db.session.query(SiskeudesRab).count()
    return jsonify(result)


@app.route('/siskeudes/rab/region/<string:region_id>', methods=['GET'])
def get_spending_budgets_by_region(region_id):
    sbs = db.session.query(SiskeudesRab) \
        .filter(SiskeudesRab.fk_region_id == region_id) \
        .all()
    result = SiskeudesRabSchema(many=True).dump(sbs)
    return jsonify(result.data)


@app.route('/siskeudes/kegiatan/', methods=['GET'])
def get_siskeudes_kegiatans():
    sks = db.session.query(SiskeudesKegiatan).all()
    result = SiskeudesKegiatanSchema(many=True).dump(sks)
    return jsonify(result.data)


@app.route('/siskeudes/kegiatan/count', methods=['GET'])
def get_siskeudes_kegiatans_count():
    result = db.session.query(SiskeudesKegiatan).count()
    return jsonify(result)


@app.route('/siskeudes/kegiatan/region/<string:region_id>', methods=['GET'])
def get_siskeudes_kegiatans_by_region(region_id):
    sks = db.session.query(SiskeudesKegiatan)\
        .filter(SiskeudesKegiatan.fk_region_id == region_id)\
        .all()
    result = SiskeudesKegiatanSchema(many=True).dump(sks)
    return jsonify(result.data)


@app.route('/generate', methods=['GET'])
def generate_all():
    generate_progress_recapitulations()
    generate_progress_timelines()
    generate_spending_types()
    generate_spending_recapitulations()
    generate_progress_revenues()
    generate_progress_spendings()


if __name__ == "__main__":
    db.create_all();
    app.run(debug=True, host=app.config["HOST"], port=app.config["KEUANGAN_PORT"])
