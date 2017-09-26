from flask import Blueprint, jsonify, request
from keuangan import db
from keuangan.models import SpendingType, SpendingTypeModelSchema, SpendingRecapitulationModelSchema
from keuangan.repository import RegionRepository, SpendingTypeRepository, SpendingRecapitulationRepository
from keuangan.helpers import QueryHelper, Generator


app = Blueprint('spending', __name__)
region_repository = RegionRepository(db)
st_repository = SpendingTypeRepository(db)
sr_repository = SpendingRecapitulationRepository(db)


@app.route('/spending/types', methods=['GET'])
def get_spending_types():
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = st_repository.all(page_sort_params)
    result = SpendingTypeModelSchema(many=True).dump(entities)
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
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = sr_repository.all(page_sort_params)
    result = SpendingRecapitulationModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/spending/recapitulations/count', methods=['GET'])
def get_spending_recapitulations_count():
    result = sr_repository.count()
    return jsonify(result)


@app.route('/spending/recapitulations/generate', methods=['GET'])
def generate_spending_recapitulations():
    regions = region_repository.all()
    spending_types = db.session.query(SpendingType).all()
    for region in regions:
        for spending_type in spending_types:
            sr = Generator.generate_spending_recapitulations()
            sr.fk_region_id = region.id
            sr.fk_type_id = spending_type.id
            db.session.add(sr)
    db.session.commit()