import logging
import traceback
from datetime import datetime
from keuangan import db
from keuangan.models import *
from keuangan.repository import *
from transformer import *

region_repository = RegionRepository(db)
sideka_content_repository = SidekaContentRepository(db)
sideka_desa_repository = SidekaDesaRepository(db)
siskeudes_kegiatan_repository = SiskeudesKegiatanRepository(db)
siskeudes_penerimaan_repository = SiskeudesPenerimaanRepository(db)
siskeudes_penerimaan_rinci_repository = SiskeudesPenerimaanRinciRepository(db)
siskeudes_penganggaran_repository = SiskeudesPenganggaranRepository(db)
siskeudes_spp_repository = SiskeudesSppRepository(db)
siskeudes_spp_bukti_repository = SiskeudesSppBuktiRepository(db)
siskeudes_spp_rinci_repository = SiskeudesSppRinciRepository(db)

logger = logging.getLogger('keuangan')


class SiskeudesFetcher:
    @staticmethod
    def fetch_desas():
        sd_desas = sideka_desa_repository.all()
        for sd_desa in sd_desas:
            if (sd_desa.kode is None or len(sd_desa.kode) == 0):
                continue

            region = region_repository.get(str(sd_desa.kode).rstrip())

            if (region is None):
                logger.warning('Desa<{0}> {1} does not have region'.format(sd_desa.desa, sd_desa.kode))
                continue

            region.domain = sd_desa.domain
            region.desa_id = sd_desa.blog_id
            region.is_lokpri = bool(sd_desa.is_lokpri)
            db.session.add(region)

    @staticmethod
    def fetch_siskeudes_codes():
        year = str(datetime.now().year)

        # Why? Because penerimaan has kode desa
        sd_contents = sideka_content_repository.get_latest_content('penerimaan', year)
        for sd_content in sd_contents:
            contents = ContentTransformer.transform(sd_content.content)
            if not ('tbp' in contents):
                logger.warning('Desa id: {0} does not have tbp'.format(sd_content.desa_id))
                continue

            sps = SiskeudesPenerimaanModelSchema(many=True).load(contents['tbp'])

            if (len(sps.data) < 1):
                continue

            has_kode_desa = getattr(sps.data[0], 'kode_desa', None);
            if (has_kode_desa is None):
                continue

            kode_desa = sps.data[0].kode_desa
            kode_desa = str(kode_desa).rstrip().rstrip('.')
            region = region_repository.get_by_desa_id(sd_content.desa_id)

            if (region is None):
                logger.warning('Desa id: {0} does not have region'.format(sd_content.desa_id))
                continue

            region.siskeudes_code = kode_desa
            db.session.add(region)

    @staticmethod
    def fetch_penganggaran_by_region(region):
        year = str(datetime.now().year)

        siskeudes_penganggaran_repository.delete_by_region_and_year(region.id, year)
        siskeudes_kegiatan_repository.delete_by_region_and_year(region.id, year)

        sd_content = sideka_content_repository.get_latest_content_by_desa_id('penganggaran', year, region.desa_id)
        if (sd_content is None):
            logger.warning('Region: {0}<{1}> does not have anggaran'.format(region.name, region.id))
            return

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
        siskeudes_penganggaran_repository.bulk_add_all(sps_data, region, year)
        siskeudes_kegiatan_repository.bulk_add_all(sks.data, region, year)

    @staticmethod
    def fetch_penerimaan_by_region(region):
        year = str(datetime.now().year)

        siskeudes_penerimaan_repository.delete_by_region_and_year(region.id, year)
        siskeudes_penerimaan_rinci_repository.delete_by_region_and_year(region.id, year)

        sd_content = sideka_content_repository.get_latest_content_by_desa_id('penerimaan', year, region.desa_id)
        if (sd_content is None):
            logger.info('Region: {0}<{1}> does not have penerimaan'.format(region.name, region.id))
            return

        contents = ContentTransformer.transform(sd_content.content)

        sps = SiskeudesPenerimaanModelSchema(many=True).load(contents['tbp'])
        sprs = SiskeudesPenerimaanRinciModelSchema(many=True).load(contents['tbp_rinci'])

        siskeudes_penerimaan_repository.bulk_add_all(sps.data, region, year)
        siskeudes_penerimaan_rinci_repository.bulk_add_all(sprs.data, region, year)

    @staticmethod
    def fetch_spp_by_region(region):
        year = str(datetime.now().year)

        siskeudes_spp_repository.delete_by_region_and_year(region.id, year)
        siskeudes_spp_bukti_repository.delete_by_region_and_year(region.id, year)
        siskeudes_spp_rinci_repository.delete_by_region_and_year(region.id, year)

        sd_content = sideka_content_repository.get_latest_content_by_desa_id('spp', year, region.desa_id)
        if (sd_content is None):
            logger.info('Region: {0}<{1}> does not have spp'.format(region.name, region.id))
            return

        contents = ContentTransformer.transform(sd_content.content)

        spps = SiskeudesSppModelSchema(many=True).load(contents['spp'])
        sppbs = SiskeudesSppBuktiModelSchema(many=True).load(contents['spp_bukti'])
        spprs = SiskeudesSppRinciModelSchema(many=True).load(contents['spp_rinci'])

        siskeudes_spp_repository.bulk_add_all(spps.data, region, year)
        siskeudes_spp_bukti_repository.bulk_add_all(sppbs.data, region, year)
        siskeudes_spp_rinci_repository.bulk_add_all(spprs.data, region, year)

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
                # TODO: Log
                traceback.print_exc()

    @staticmethod
    def fetch_spps():
        regions = region_repository.all()
        for region in regions:
            try:
                print "Error on region %s - %s" % (region.id, region.name)
                SiskeudesFetcher.fetch_spp_by_region(region)
            except Exception as e:
                # TODO: Log
                traceback.print_exc()
