from datetime import datetime
from keuangan import db
from keuangan.models import SpendingType
from keuangan.repository import *
from transformer import ProgressRecapitulationTransformer, ProgressTimelineTransformer, \
    SpendingRecapitulationTransformer

region_repository = RegionRepository(db)
progress_recapitulation_repository = ProgressRecapitulationRepository(db)
progress_timeline_repository = ProgressTimelineRepository(db)
siskeudes_penganggaran_repository = SiskeudesPenganggaranRepository(db)
siskeudes_penerimaan_rinci_repository = SiskeudesPenerimaanRinciRepository(db)
siskeudes_spp_rinci_repository = SiskeudesSppRinciRepository(db)
spending_recapitulation_repository = SpendingRecapitulationRepository(db)
spending_type_repository = SpendingTypeRepository(db)


class Generator:
    @staticmethod
    def generate_progress_recapitulation_by_region(region):
        year = datetime.now().year
        progress_recapitulation_repository.delete_by_region(region.id)
        anggarans = siskeudes_penganggaran_repository.get_by_region(region.id)
        penerimaan_rincis = siskeudes_penerimaan_rinci_repository.get_by_region(region.id)
        spp_rincis = siskeudes_spp_rinci_repository.get_by_region(region.id)

        result = ProgressRecapitulationTransformer.transform(anggarans, penerimaan_rincis, spp_rincis, year, region)
        return result

    @staticmethod
    def generate_progress_timeline_by_region(region):
        year = datetime.now().year
        progress_timeline_repository.delete_by_region(region.id)
        penerimaan_rincis = siskeudes_penerimaan_rinci_repository.get_by_region(region.id)
        spp_rincis = siskeudes_spp_rinci_repository.get_by_region(region.id)

        result = ProgressTimelineTransformer.transform(penerimaan_rincis, spp_rincis, year, region)
        return result

    @staticmethod
    def generate_spending_recapitulation_by_region(region):
        year = datetime.now().year
        spending_types = spending_type_repository.all()
        spending_recapitulation_repository.delete_by_region(region.id)
        anggarans = siskeudes_penganggaran_repository.get_by_region(region.id)

        result = SpendingRecapitulationTransformer.transform(anggarans, year, region, spending_types)
        return result

    @staticmethod
    def generate_progress_recapitulations():
        result = []
        regions = region_repository.all()
        for region in regions:
            pr = Generator.generate_progress_recapitulation_by_region(region)
            result.append(pr)
        return result

    @staticmethod
    def generate_progress_timelines():
        result = []
        regions = region_repository.all()
        for region in regions:
            pts = Generator.generate_progress_timeline_by_region(region)
            result += pts
        return result

    @staticmethod
    def generate_spending_recapitulations():
        result = []
        regions = region_repository.all()
        for region in regions:
            srs = Generator.generate_spending_recapitulation_by_region(region)
            result += srs
        return result

    @staticmethod
    def generate_spending_types():
        result = []
        spending_types = [('19.16.01', 'Penyelengaraan Pemerintahan Desa'),
                          ('19.16.02', 'Pelaksanaan Pembangunan Desa'),
                          ('19.16.03', 'Pembinaan Kemasyarakatan'),
                          ('19.16.04', 'Pemberdayaan Masyarakat')]
        for spending_type in spending_types:
            st = SpendingType()
            st.code = spending_type[0]
            st.name = spending_type[1]
            result.append(st)
        return result
