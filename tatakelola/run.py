import os, logging
from logging.handlers import RotatingFileHandler
from flask import request, jsonify
from common import gzipped
from tatakelola import create_app, db
from tatakelola.helpers import TatakelolaFetcher, QueryHelper
from tatakelola.models import Region, RegionModelSchema, Geojson, GeojsonModelSchema, Data, DataModelSchema

app = create_app()


@app.route('/regions', methods=['GET'])
def get_regions():
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    query = db.session.query(Region).filter(Region.is_lokpri == True)
    query = QueryHelper.build_page_sort_query(query, Region, page_sort_params)
    regions = query.all()
    result = RegionModelSchema(many=True).dump(regions)
    return jsonify(result.data)


@app.route('/regions/count', methods=['GET'])
def get_regions_count():
    result = db.session.query(Region).count()
    return jsonify(result)


@app.route('/regions/<string:id>', methods=['GET'])
def get_region(id):
    region = db.session.query(Region).filter(Region.id == id).first()
    result = RegionModelSchema(many=False).dump(region)
    return jsonify(result.data)


@app.route('/geojsons/region/<string:region_id>', methods=['GET'])
@gzipped
def get_geojsons_by_region_id(region_id):
    geojsons = db.session.query(Geojson).filter(Geojson.fk_region_id == region_id).all()
    result = GeojsonModelSchema(many=True).dump(geojsons)
    return jsonify(result.data)


@app.route('/geojsons/type/<string:type>/region/<string:region_id>', methods=['GET'])
def get_geojson_by_type_and_region_id(type, region_id):
    geojson = db.session.query(Geojson).filter(Geojson.type == type).filter(Geojson.fk_region_id == region_id).first()
    result = GeojsonModelSchema(many=False).dump(geojson)
    return jsonify(result.data)


@app.route('/data/region/<string:region_id>', methods=['GET'])
def get_data_by_region_id(region_id):
    data = db.session.query(Data).filter(Data.fk_region_id == region_id)
    result = DataModelSchema(many=False).dump(data)
    return jsonify(result.data)


@app.route('/admin/fetch/geojsons', methods=['GET'])
def fetch_geojsons():
    TatakelolaFetcher.fetch_geojsons()
    return jsonify({'success': True})


@app.route('/admin/fetch/data', methods=['GET'])
def fetch_data():
    TatakelolaFetcher.fetch_data()
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


if __name__ == "__main__":
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'tatakelola.log')
    handler = RotatingFileHandler(log_file, maxBytes=1000000, backupCount=5)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    app.run(debug=True, host=app.config["HOST"], port=app.config["TATAKELOLA_PORT"])
