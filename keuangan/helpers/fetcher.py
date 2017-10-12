from datetime import datetime
from keuangan import db
from keuangan.models import *
from keuangan.repository import *
from transformer import *
import traceback

region_repository = RegionRepository(db)
sideka_content_repository = SidekaContentRepository(db)
siskeudes_kegiatan_repository = SiskeudesKegiatanRepository(db)
siskeudes_penerimaan_repository = SiskeudesPenerimaanRepository(db)
siskeudes_penerimaan_rinci_repository = SiskeudesPenerimaanRinciRepository(db)
siskeudes_penganggaran_repository = SiskeudesPenganggaranRepository(db)
siskeudes_spp_repository = SiskeudesSppRepository(db)
siskeudes_spp_bukti_repository = SiskeudesSppBuktiRepository(db)
siskeudes_spp_rinci_repository = SiskeudesSppRinciRepository(db)


class SiskeudesFetcher:
    @staticmethod
    def fetch_penganggaran_by_region(region):
        year = str(datetime.now().year)

        # delete penganggaran and kegiatan
        siskeudes_penganggaran_repository.delete_by_region(region.id)
        siskeudes_kegiatan_repository.delete_by_region(region.id)

        sd_content = sideka_content_repository.get_latest_content_by_desa_id('penganggaran', year, region.desa_id)
        contents = ContentTransformer.transform(sd_content.content)

        i = 1
        for content_rab in contents['rab']:
            content_rab['row_number'] = i
            i += 1

            # Hack, why? because there is an empty string instead of null
            if isinstance(content_rab['perubahan'], basestring):
                content_rab['perubahan'] = None
            if isinstance(content_rab['jumlah_satuan'], basestring):
                content_rab['jumlah_satuan'] = None
            if isinstance(content_rab['harga_satuan'], basestring):
                content_rab['harga_satuan'] = None
            if isinstance(content_rab['jumlah_satuan_pak'], basestring):
                content_rab['jumlah_satuan_pak'] = None
            if isinstance(content_rab['harga_satuan_pak'], basestring):
                content_rab['harga_satuan_pak'] = None

        sps = SiskeudesPenganggaranModelSchema(many=True).load(contents['rab'])
        sps_data = SiskeudesPenganggaranTransformer.transform(sps.data)
        sks = SiskeudesKegiatanModelSchema(many=True).load(contents['kegiatan'])
        siskeudes_penganggaran_repository.add_all(sps_data, region, year)
        siskeudes_kegiatan_repository.add_all(sks.data, region, year)


    @staticmethod
    def fetch_penerimaan_by_region(region):
        year = str(datetime.now().year)

        # delete penerimaan and penerimaan rincis
        siskeudes_penerimaan_repository.delete_by_region(region.id)
        siskeudes_penerimaan_rinci_repository.delete_by_region(region.id)

        sd_content = sideka_content_repository.get_latest_content_by_desa_id('penerimaan', year, region.desa_id)
        contents = ContentTransformer.transform(sd_content.content)

        sps = SiskeudesPenerimaanModelSchema(many=True).load(contents['tbp'])
        sprs = SiskeudesPenerimaanRinciModelSchema(many=True).load(contents['tbp_rinci'])

        siskeudes_penerimaan_repository.add_all(sps.data, region, year)
        siskeudes_penerimaan_rinci_repository.add_all(sprs.data, region, year)

    @staticmethod
    def fetch_spp_by_region(region):
        year = str(datetime.now().year)

        # delete spp, spp bukti and spp rinci
        siskeudes_spp_repository.delete_by_region(region.id)
        siskeudes_spp_bukti_repository.delete_by_region(region.id)
        siskeudes_spp_rinci_repository.delete_by_region(region.id)

        sd_content = sideka_content_repository.get_latest_content_by_desa_id('spp', year, region.desa_id)
        contents = ContentTransformer.transform(sd_content.content)

        spps = SiskeudesSppModelSchema(many=True).load(contents['spp'])
        sppbs = SiskeudesSppBuktiModelSchema(many=True).load(contents['spp_bukti'])
        spprs = SiskeudesSppRinciModelSchema(many=True).load(contents['spp_rinci'])

        siskeudes_spp_repository.add_all(spps.data, region, year)
        siskeudes_spp_bukti_repository.add_all(sppbs.data, region, year)
        siskeudes_spp_rinci_repository.add_all(spprs.data, region, year)

    @staticmethod
    def fetch_penganggarans():
        regions = region_repository.all()
        for region in regions:
            try:
                SiskeudesFetcher.fetch_penganggaran_by_region(region)
            except Exception as e:
                print "Error on region %s - %s" % (region.id, region.name)
            	traceback.print_exc()

    @staticmethod
    def fetch_penerimaans():
        regions = region_repository.all()
        for region in regions:
            try:
                print "Error on region %s - %s" % (region.id, region.name)
            	SiskeudesFetcher.fetch_penerimaan_by_region(region)
            except Exception as e:
            	traceback.print_exc()

    @staticmethod
    def fetch_spps():
        regions = region_repository.all()
        for region in regions:
            try:
                print "Error on region %s - %s" % (region.id, region.name)
                SiskeudesFetcher.fetch_spp_by_region(region)
            except Exception as e:
            	traceback.print_exc()
