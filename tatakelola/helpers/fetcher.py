import logging, traceback
from tatakelola import db
from tatakelola.models import Geojson, Data, PendudukModelSchema, Apbdes, Penduduk
from tatakelola.repository import RegionRepository, SidekaContentRepository, SidekaDesaRepository, \
    DataRepository, GeojsonRepository, ProgressRecapitulationRepository, ApbdesRepository, PendudukRepository
from transformer import ContentTransformer, PemetaanContentTransformer, GeojsonTransformer
from datetime import datetime

region_repository = RegionRepository(db)
sideka_content_repository = SidekaContentRepository(db)
sideka_desa_repository = SidekaDesaRepository(db)
data_repository = DataRepository(db)
geojson_repository = GeojsonRepository(db)
progress_recapitulation_repository = ProgressRecapitulationRepository(db)
apbdes_repository = ApbdesRepository(db)
penduduk_repository = PendudukRepository(db)

logger = logging.getLogger('tatakelola')


class TatakelolaFetcher():
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
            region_repository.add(region)

    @staticmethod
    def fetch_geojsons_by_region(region):
        geojson_repository.delete_by_region(region.id)

        sd_content = sideka_content_repository.get_latest_content_by_desa_id('pemetaan', None, region.desa_id)
        if (sd_content is None):
            logger.warning('Region: {0}<{1}><{2}> does not have geojsons'.format(region.name, region.id, region.desa_id))
            return

        contents = PemetaanContentTransformer.transform(sd_content.content)
        for content in contents:
            data = GeojsonTransformer.transform(contents[content])
            geo = Geojson()
            geo.type = content
            geo.data = data
            geo.fk_region_id = region.id
            geojson_repository.add(geo)

    @staticmethod
    def fetch_data_by_region(region):
        data_repository.delete_by_region(region.id)
        penduduk_repository.delete_by_region(region.id)

        penduduk_sd_content = sideka_content_repository.get_latest_content_by_desa_id('penduduk', None, region.desa_id)
        
        if (penduduk_sd_content is None):
            logger.warning('Region: {0}<{1}><{2}> does not have penduduk'.format(region.name, region.id, region.desa_id))
            return

        contents = ContentTransformer.transform(penduduk_sd_content.content)
        
        if (contents is None):
            logger.warning('Region: {0}<{1}><{2}> does not have correct penduduk'.format(region.name, region.id, region.desa_id))
            return

        data = Data()
        data.fk_region_id = None
        data.data = {'penduduk': contents['penduduk']}
        data.fk_region_id = region.id
        data_repository.add(data)

        penduduks = []

        for d in contents['penduduk']:
            penduduk = Penduduk()
            penduduk.id = d['id']
            penduduk.nik = d['nik']
            penduduk.nama_penduduk = d['nama_penduduk']
            penduduk.jenis_kelamin = d['jenis_kelamin']
            penduduk.tempat_lahir = d['tempat_lahir']

            if penduduk.tanggal_lahir != None:
                penduduk.tanggal_lahir = datetime.strptime(d['tanggal_lahir'], '%d/%m/%Y') 

            penduduk.status_kawin = d['status_kawin']
            penduduk.agama = d['agama']
            penduduk.golongan_darah = d['golongan_darah']
            penduduk.kewarganegaraan = d['kewarganegaraan']
            penduduk.no_kk = d['no_kk']
            penduduk.nama_ayah = d['nama_ayah']
            penduduk.nama_ibu = d['nama_ibu']
            penduduk.hubungan_keluarga = d['hubungan_keluarga']
            penduduk.nama_dusun = d['nama_dusun']
            penduduk.rw = d['rw']
            penduduk.rt = d['rt']
            penduduk.alamat_jalan = d['alamat_jalan']
            penduduk.no_telepon = d['no_telepon']
            penduduk.email = d['email']
            penduduk.no_akta = d['no_akta']
            penduduk.no_kitas = d['no_kitas']
            penduduk.no_paspor = d['no_paspor']
            penduduk.pendidikan = d['pendidikan']
            penduduk.pekerjaan = d['pekerjaan']
            penduduk.etnis_suku = d['etnis_suku']
            penduduk.status_tinggal = d['status_tinggal']
            penduduk.akseptor_kb = d['akseptor_kb']
            penduduk.cacat_fisik = d['cacat_fisik']
            penduduk.cacat_mental = d['cacat_mental']
            penduduk.wajib_pajak = d['wajib_pajak']
            penduduk.lembaga_pemerintahan = d['lembaga_pemerintahan']
            penduduk.lembaga_kemasyarakatan = d['lembaga_kemasyarakatan']
            penduduk.lembaga_ekonomi = d['lembaga_ekonomi']
            penduduk.fk_region_id = region.id
            penduduk.region = region
            penduduks.append(penduduk)
       
        #penduduks = PendudukModelSchema(many=True).load(contents['penduduk'])
        
        #for penduduk in penduduks.data:
            #penduduk.fk_region_id = region.id
        penduduk_repository.bulk_add_all(penduduks)

    @staticmethod
    def fetch_apbdes_by_region(region):
        apbdes_repository.delete_by_region(region.id)

        apbdeses = []
        prs = progress_recapitulation_repository.get_by_region(region.id)
        if (not prs):
            logger.warning('Region: {0}<{1}><{2}> does not have apbdes'.format(region.name, region.id, region.desa_id))
            return

        for pr in prs:
            apbdes = Apbdes()
            apbdes.budgeted_revenue = pr.budgeted_revenue
            apbdes.transferred_revenue = pr.transferred_revenue
            apbdes.budgeted_spending = pr.budgeted_spending
            apbdes.realized_spending = pr.realized_spending
            apbdes.year = pr.year
            apbdes.fk_region_id = pr.fk_region_id
            apbdeses.append(apbdes)

        apbdes_repository.add_all(apbdeses)

    @staticmethod
    def fetch_geojsons():
        regions = region_repository.all()
        for region in regions:
            try:
                TatakelolaFetcher.fetch_geojsons_by_region(region)
            except Exception as e:
                logger.error("Region: {0}<{1}><{2}>".format(region.name, region.id, region.desa_id))
                logger.error(e.message)
                traceback.print_exc()

    @staticmethod
    def fetch_data():
        regions = region_repository.all()
        #regions = list()
        #regions.append(region_repository.get_by_desa_id(3))
        for region in regions:
            try:
                TatakelolaFetcher.fetch_data_by_region(region)
            except Exception as e:
                logger.error("Region: {0}<{1}><{2}>".format(region.name, region.id, region.desa_id))
                logger.error(e.message)
                traceback.print_exc()

    @staticmethod
    def fetch_apbdes():
        regions = region_repository.all()
        for region in regions:
            try:
                TatakelolaFetcher.fetch_apbdes_by_region(region)
            except Exception as e:
                logger.error("Region: {0}<{1}><{2}>".format(region.name, region.id, region.desa_id))
                logging.error(e.message)
                traceback.print_exc()

    @staticmethod
    def fetch_mandalamekar():
        region = region_repository.get('32.06.19.2009')
        try:
            TatakelolaFetcher.fetch_data_by_region(region)
        except Exception as e:
            logger.error("Region: {0}<{1}><{2}>".format(region.name, region.id, region.desa_id))
            logger.error(e.message)
            traceback.print_exc()
        
