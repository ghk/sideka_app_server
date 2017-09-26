from flask import Blueprint, jsonify, request
from keuangan import db
from keuangan.models import ProgressRecapitulationModelSchema, ProgressTimelineModelSchema
from keuangan.repository import RegionRepository, ProgressRecapitulationRepository, ProgressTimelineRepository
from keuangan.helpers import QueryHelper, Generator


app = Blueprint('progress', __name__)
region_repository = RegionRepository(db)
progress_recapitulation_repository = ProgressRecapitulationRepository(db)
progress_timeline_repository = ProgressTimelineRepository(db)


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
    regions = region_repository.all()
    months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    for region in regions:
        for month in months:
            pt = Generator.generate_progress_timeline()
            pt.month = month
            pt.fk_region_id = region.id
            db.session.add(pt)
    db.session.commit()