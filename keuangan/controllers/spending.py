from flask import Blueprint, jsonify, request
from keuangan import db
from keuangan.models import SpendingType, SpendingTypeModelSchema, SpendingRecapitulationModelSchema
from keuangan.repository import RegionRepository, SpendingTypeRepository, SiskeudesPenganggaranRepository
from keuangan.repository import SpendingRecapitulationRepository
from keuangan.helpers import QueryHelper, SpendingRecapitulationTransformer
from datetime import datetime

app = Blueprint('spending', __name__)
region_repository = RegionRepository(db)
sp_repository = SiskeudesPenganggaranRepository(db)
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
    spending_types = [('19.16.01', 'Penyelengaraan Pemerintahan Desa'),
                      ('19.16.02', 'Pelaksanaan Pembangunan Desa'),
                      ('19.16.03', 'Pembinaan Kemasyarakatan'),
                      ('19.16.04', 'Pemberdayaan Masyarakat')]
    for spending_type in spending_types:
        st = SpendingType()
        st.code = spending_type[0];
        st.name = spending_type[1];
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
    year = datetime.now().year
    regions = region_repository.all()
    spending_types = st_repository.all()
    for region in regions:
        sr_repository.delete_by_region(region.id)
        anggarans = sp_repository.get_by_region(region.id)
        srs = SpendingRecapitulationTransformer.transform(anggarans, year, region, spending_types)
        db.session.add_all(srs)
    db.session.commit()