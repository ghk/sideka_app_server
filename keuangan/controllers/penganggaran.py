from flask import Blueprint, jsonify, request
from datetime import datetime
from keuangan import db
from keuangan.models import SiskeudesPenganggaranModelSchema
from keuangan.models import SiskeudesKegiatanModelSchema
from keuangan.repository import RegionRepository, SidekaContentRepository
from keuangan.repository import SiskeudesPenganggaranRepository, SiskeudesKegiatanRepository
from keuangan.helpers import QueryHelper, ContentTransformer

app = Blueprint('penganggaran', __name__)
region_repository = RegionRepository(db)
sideka_content_repository = SidekaContentRepository(db)
siskeudes_penganggaran_repository = SiskeudesPenganggaranRepository(db)
siskeudes_kegiatan_repository = SiskeudesKegiatanRepository(db)


@app.route('/siskeudes/penganggarans', methods=['GET'])
def get_siskeudes_penganggarans():
    page_sort_params = QueryHelper.get_page_sort_params_from_request(request)
    entities = siskeudes_penganggaran_repository.all(page_sort_params)
    result = SiskeudesPenganggaranModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/penganggarans/count', methods=['GET'])
def get_siskeudes_penganggarans_count():
    result = siskeudes_penganggaran_repository.count()
    return jsonify(result)


@app.route('/siskeudes/penganggarans/region/<string:region_id>', methods=['GET'])
def get_siskeudes_penganggarans_by_region(region_id):
    entities = siskeudes_penganggaran_repository.get_by_region(region_id)
    result = SiskeudesPenganggaranModelSchema(many=True).dump(entities)
    return jsonify(result.data)


@app.route('/siskeudes/penganggarans/fetch', methods=['GET'])
def fetch_siskeudes_penganggarans():
    year = str(datetime.now().year)
    regions = region_repository.all()

    for region in regions:
        siskeudes_penganggaran_repository.delete_by_region(region.id)
        siskeudes_kegiatan_repository.delete_by_region(region.id)
        sd_content = sideka_content_repository.get_latest_content_by_desa_id('penganggaran', year, region.desa_id)
        contents = ContentTransformer.transform(sd_content.content)

        # Hack
        for content_rab in contents['rab']:
            if not bool(content_rab['perubahan'] and content_rab['perubahan'].strip()):
                content_rab['perubahan'] = None

        sps = SiskeudesPenganggaranModelSchema(many=True).load(contents['rab'])
        sks = SiskeudesKegiatanModelSchema(many=True).load(contents['kegiatan'])
        siskeudes_penganggaran_repository.add_all(sps.data, region, year)
        siskeudes_kegiatan_repository.add_all(sks.data, region, year)

    return jsonify({'success': True})

