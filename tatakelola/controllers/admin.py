from flask import Blueprint, jsonify, current_app
from time import time
from tatakelola import db
from tatakelola.helpers import TatakelolaFetcher, Generator

app = Blueprint('admin', __name__)

# @app.route('/admin/fetch/mandalamekar', methods=['GET'])
# def fetch_mandalameker():
#     TatakelolaFetcher.fetch_mandalamekar()
#     db.session.commit()
#     current_app.logger.info('Fetch Total Time: ' + str(time() - t0) + ' seconds')
#     return jsonify({'success': True})

@app.route('/admin/fetch/desas', methods=['GET'])
def fetch_desa_ids():
    t0 = time()
    TatakelolaFetcher.fetch_desas()
    db.session.commit()
    current_app.logger.info('Fetch Siskeudes Desa Id Total Time: ' + str(time() - t0) + ' seconds')
    return jsonify({'success': True})

@app.route('/admin/fetch/all', methods=['GET'])
def fetch_all():
    t0 = time()
    #TatakelolaFetcher.fetch_desas()
    #TatakelolaFetcher.fetch_geojsons('18.05')
    TatakelolaFetcher.fetch_data('18.05')
    #TatakelolaFetcher.fetch_apbdes('18.05')
    db.session.commit()
    #current_app.logger.info('Fetch Total Time: ' + str(time() - t0) + ' seconds')
    return jsonify({'success': True})

@app.route('/admin/generate/all', methods=['GET'])
def generate_all():
    t0 = time()
    summaries = Generator.generate_summaries('18.05')

    # TODO: Improve speed by using bulk_save_objects
    db.session.add_all(summaries)
    db.session.commit()
    current_app.logger.info('Generate Total Time: ' + str(time() - t0) + ' seconds')
    return jsonify({'success': True})

@app.route('/admin/generate/layouts', methods=['GET'])
def generate_layouts():
    t0 = time()
    layouts = Generator.generate_layouts('18.05')

    db.session.add_all(layouts)
    db.session.commit()
    current_app.logger.info('Generate Total Time: ' + str(time() - t0) + ' seconds')
    return jsonify({'success': True})

@app.route('/admin/generate/boundaries', methods=['GET'])
def generate_boundaries():
    t0 = time()
    boundary = Generator.generate_boundaries('18.05')

    db.session.add(boundary)
    db.session.commit()
    current_app.logger.info('Generate Total Time: ' + str(time() - t0) + ' seconds')
    return jsonify({'success': True})

@app.route('/admin/test', methods=['GET'])
def test():
    query1 = '\'{"id": "oQM8YJSEHLDpTKrkfkZO9k"}\''
    query2 = '\'{"id": "h5Gs6TfCIha.7HKyUeNitk"}\''
    query = ','.join([query1, query2])
    raw_query = "SELECT geojsons.fk_region_id, features FROM geojsons, jsonb_array_elements(data->'features') features WHERE features @> ANY (ARRAY[{0}]::jsonb[])".format(
        query)
    result_proxy = db.engine.execute(raw_query)
    result = []
    for row in result_proxy:
        result.append([row[0], row[1]])
    return jsonify(result)
