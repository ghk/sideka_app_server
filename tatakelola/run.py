from flask import request, jsonify
from common import gzipped
from tatakelola import create_app, db
from tatakelola.helpers import TatakelolaFetcher, QueryHelper
from tatakelola.models import Region, RegionModelSchema, Geojson, GeojsonModelSchema

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


@app.route('/admin/fetch/geojsons', methods=['GET'])
def fetch_geojsons():
    TatakelolaFetcher.fetch_geojsons()


if __name__ == "__main__":
    app.run(debug=True, host=app.config["HOST"], port=app.config["TATAKELOLA_PORT"])
