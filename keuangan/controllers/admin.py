from flask import Blueprint, jsonify, current_app
from time import time
from keuangan import db, cache
from keuangan.helpers import SiskeudesFetcher, Generator
from keuangan.repository import RegionRepository

app = Blueprint('admin', __name__)
region_repository = RegionRepository(db)


@app.route('/admin/fetch/desas', methods=['GET'])
def fetch_desas():
    t0 = time()
    SiskeudesFetcher.fetch_desas()
    db.session.commit()
    current_app.logger.info('Fetch Siskeudes Desa Id Total Time: ' + str(time() - t0) + ' seconds')
    return jsonify({'success': True})


@app.route('/admin/fetch/siskeudes_codes', methods=['GET'])
def fetch_siskeudes_codes():
    t0 = time()
    SiskeudesFetcher.fetch_siskeudes_codes()
    db.session.commit()
    current_app.logger.info('Fetch Siskeudes Code Total Time: ' + str(time() - t0) + ' seconds')
    return jsonify({'success': True})


@app.route('/admin/fetch/all/year/<string:year>', methods=['GET'])
def fetch_all(year):
    t0 = time()

    SiskeudesFetcher.fetch_desas()
    SiskeudesFetcher.fetch_siskeudes_codes_by_year(year)
    SiskeudesFetcher.fetch_penerimaans_by_year(year)
    SiskeudesFetcher.fetch_penganggarans_by_year(year)
    SiskeudesFetcher.fetch_spps_by_year(year)

    db.session.commit()

    clear_cache()
    current_app.logger.info('Fetch Total Time: ' + str(time() - t0) + ' seconds')
    return jsonify({'success': True})


@app.route('/admin/generate/all/year/<string:year>', methods=['GET'])
def generate_all(year):
    t0 = time()

    prs = Generator.generate_progress_recapitulations_by_year(year)
    pts = Generator.generate_progress_timelines_by_year(year)
    srs = Generator.generate_budget_recapitulations_by_year(year)
    sls = Generator.generate_siskeudes_likelihood_by_year(year)

    # TODO: Improve speed by using bulk_save_objects
    db.session.add_all(prs)
    db.session.add_all(pts)
    db.session.add_all(srs)
    db.session.add_all(sls)
    db.session.commit()

    clear_cache()
    current_app.logger.info('Generate Total Time: ' + str(time() - t0) + ' seconds')
    return jsonify({'success': True})


@app.route('/admin/cache/clear', methods=['GET'])
def clear_cache():
    cache.clear()


@app.route('/admin/run/all', methods=['GET'])
def run_all():
    year = '2017'
    fetch_result = fetch_all(year)
    generate_result = generate_all(year)
    return generate_result


@app.route('/budget/types/generate', methods=['GET'])
def generate_budget_types():
    budget_types = Generator.generate_budget_types()
    db.session.add_all(budget_types)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/budget/recapitulations/year/<string:year>/generate', methods=['GET'])
def generate_budget_recapitulations_by_year(year):
    entities = Generator.generate_budget_recapitulations_by_year(year)
    db.session.add_all(entities)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/budget/recapitulations/region/<string:region_id>/year/<string:year>/generate', methods=['GET'])
def generate_budget_recapitulation_by_region_and_year(region_id, year):
    region = region_repository.get(region_id)
    entity = Generator.generate_budget_recapitulation_by_region_and_year(region, year)
    db.session.add(entity)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/siskeudes/penganggarans/fetch/year/<string:year>', methods=['GET'])
def fetch_siskeudes_penganggarans(year):
    SiskeudesFetcher.fetch_penganggarans_by_year(year)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/siskeudes/penganggarans/fetch/region/<string:region_id>/year/<string:year>', methods=['GET'])
def fetch_siskeudes_penganggarans_by_region(region_id, year):
    region = region_repository.get(region_id)
    SiskeudesFetcher.fetch_penganggarans_by_region_and_year(region, year)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/progress/recapitulations/generate/year/<string:year>', methods=['GET'])
def generate_progress_recapitulations_by_year(year):
    progress_recapitulations = Generator.generate_progress_recapitulations_by_year(year)
    db.session.add_all(progress_recapitulations)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/progress/recapitulations/generate/region/<string:region_id>/year/<string:year>', methods=['GET'])
def generate_progress_recapitulation_by_region_and_year(region_id, year):
    region = region_repository.get(region_id)
    progress_recapitulation = Generator.generate_progress_recapitulation_by_region_and_year(region, year)
    db.session.add(progress_recapitulation)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/progress/timelines/generate/year/<string:year>', methods=['GET'])
def generate_progress_timelines_by_year(year):
    progress_timelines = Generator.generate_progress_timelines_by_year(year)
    db.session.add_all(progress_timelines)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/siskeudes/spps/fetch/year/<string:year>', methods=['GET'])
def fetch_siskeudes_spps(year):
    SiskeudesFetcher.fetch_spps_by_year(year)
    db.session.commit()
    return jsonify({'success': True})
