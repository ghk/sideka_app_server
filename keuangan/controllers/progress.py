from flask import Blueprint, jsonify, request
from keuangan import db
from keuangan.models import ProgressRecapitulationModelSchema, ProgressTimelineModelSchema
from keuangan.repository import RegionRepository, ProgressRecapitulationRepository, ProgressTimelineRepository
from keuangan.repository import SiskeudesSppRinciRepository, SiskeudesPenerimaanRinciRepository
from keuangan.helpers import QueryHelper, Generator, ProgressTimelineTransformer
from datetime import datetime


app = Blueprint('progress', __name__)
region_repository = RegionRepository(db)
progress_recapitulation_repository = ProgressRecapitulationRepository(db)
progress_timeline_repository = ProgressTimelineRepository(db)
siskeudes_spp_rinci_repository = SiskeudesSppRinciRepository(db)
siskeudes_penerimaan_rinci_repository = SiskeudesPenerimaanRinciRepository(db)

@app.route('/progress/recapitulations', methods=['GET'])
def get_progress_recapitulations():
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = progress_recapitulation_repository.all(page_sort_params)
    result = ProgressRecapitulationModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/progress/recapitulations/count', methods=['GET'])
def get_progress_recapitulations_count():
    result = progress_recapitulation_repository.count()
    return jsonify(result)


@app.route('/progress/recapitulations/generate', methods=['GET'])
def generate_progress_recapitulations():
    regions = region_repository.all()
    for region in regions:
        pr = Generator.generate_progress_recapitulation()
        pr.fk_region_id = region.id
        db.session.add(pr)
    db.session.commit()


@app.route('/progress/timelines', methods=['GET'])
def get_progress_timelines():
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = progress_timeline_repository.all(page_sort_params)
    result = ProgressTimelineModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/progress/timelines/count', methods=['GET'])
def get_progress_timelines_count():
    result = progress_timeline_repository.count()
    return jsonify(result)


@app.route('/progress/timelines/region/<string:region_id>', methods=['GET'])
def get_progress_timelines_by_region(region_id):
    entities = progress_timeline_repository.get_by_region(region_id)
    result = ProgressTimelineModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/progress/timelines/generate', methods=['GET'])
def generate_progress_timelines():
    year = datetime.now().year
    regions = region_repository.all()

    for region in regions:
        progress_timeline_repository.delete_by_region(region.id)
        penerimaan_rincis = siskeudes_penerimaan_rinci_repository.get_by_region(region.id)
        spp_rincis = siskeudes_spp_rinci_repository.get_by_region(region.id)
        pts = ProgressTimelineTransformer.transform(penerimaan_rincis, spp_rincis, year, region)
        db.session.add_all(pts)

    db.session.commit()
