from flask import Blueprint, jsonify, request
from keuangan import db
from keuangan.models import ProgressRecapitulationModelSchema, ProgressTimelineModelSchema
from keuangan.repository import ProgressRecapitulationRepository, ProgressTimelineRepository
from keuangan.helpers import QueryHelper, Generator

app = Blueprint('progress', __name__)
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
    progress_recapitulations = Generator.generate_progress_recapitulation()
    db.session.add_all(progress_recapitulations)
    db.session.commit()
    return jsonify({'success': True})


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
    progress_timelines = Generator.generate_progress_timeline()
    db.session.add_all(progress_timelines)
    db.session.commit()
    return jsonify({'success': True})
