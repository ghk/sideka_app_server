from keuangan import db
from keuangan.models import BudgetType
from keuangan.repository import *
from transformer import ProgressRecapitulationTransformer, ProgressTimelineTransformer, \
    BudgetRecapitulationTransformer, SiskeudesLikelihoodTransformer

region_repository = RegionRepository(db)
progress_recapitulation_repository = ProgressRecapitulationRepository(db)
progress_timeline_repository = ProgressTimelineRepository(db)
siskeudes_penganggaran_repository = SiskeudesPenganggaranRepository(db)
siskeudes_penerimaan_rinci_repository = SiskeudesPenerimaanRinciRepository(db)
siskeudes_spp_rinci_repository = SiskeudesSppRinciRepository(db)
budget_recapitulation_repository = BudgetRecapitulationRepository(db)
budget_type_repository = BudgetTypeRepository(db)
siskeudes_likelihood_repository = BudgetLikelihoodRepository(db)
view_learn_kegiatan_repository = ViewLearnKegiatanRepository(db)


class Generator:
    @staticmethod
    def generate_progress_recapitulation_by_region_and_year(region, year):
        progress_recapitulation_repository.delete_by_region_and_year(region.id, year)

        anggarans = siskeudes_penganggaran_repository.get_by_region_and_year(region.id, year)
        penerimaan_rincis = siskeudes_penerimaan_rinci_repository.get_by_region_and_year(region.id, year)
        spp_rincis = siskeudes_spp_rinci_repository.get_by_region_and_year(region.id, year)

        result = ProgressRecapitulationTransformer.transform(anggarans, penerimaan_rincis, spp_rincis, year, region)
        return result

    @staticmethod
    def generate_progress_timeline_by_region_and_year(region, year):
        progress_timeline_repository.delete_by_region_and_year(region.id, year)

        penerimaan_rincis = siskeudes_penerimaan_rinci_repository.get_by_region_and_year(region.id, year)
        spp_rincis = siskeudes_spp_rinci_repository.get_by_region_and_year(region.id, year)

        result = ProgressTimelineTransformer.transform(penerimaan_rincis, spp_rincis, year, region)
        return result

    @staticmethod
    def generate_budget_recapitulation_by_region_and_year(region, year):
        budget_recapitulation_repository.delete_by_region_and_year(region.id, year)

        budget_types = budget_type_repository.all()
        anggarans = siskeudes_penganggaran_repository.get_by_region_and_year(region.id, year)

        result = BudgetRecapitulationTransformer.transform(anggarans, year, region, budget_types)
        return result

    @staticmethod
    def generate_progress_recapitulations_by_year(year):
        result = []
        regions = region_repository.all(is_lokpri=False, is_siskeudes_code=True)
        for region in regions:
            pr = Generator.generate_progress_recapitulation_by_region_and_year(region, year)
            result.append(pr)
        return result

    @staticmethod
    def generate_progress_timelines_by_year(year):
        result = []
        regions = region_repository.all(is_lokpri=False, is_siskeudes_code=True)
        for region in regions:
            pts = Generator.generate_progress_timeline_by_region_and_year(region, year)
            result += pts
        return result

    @staticmethod
    def generate_budget_recapitulations_by_year(year):
        result = []
        regions = region_repository.all(is_lokpri=False, is_siskeudes_code=True)
        for region in regions:
            srs = Generator.generate_budget_recapitulation_by_region_and_year(region, year)
            result += srs
        return result

    @staticmethod
    def generate_siskeudes_likelihood_by_year(year):
        siskeudes_likelihood_repository.delete_by_year(year)

        model = view_learn_kegiatan_repository.model
        view_learn_kegiatan_query = db.session.query(model) \
            .filter(model.year == year)

        result = SiskeudesLikelihoodTransformer.transform(view_learn_kegiatan_query, year)
        return result

    @staticmethod
    def generate_budget_types():
        result = []
        budget_types = [
            ('DDS', 'Dana Desa', True),
            ('ADD', 'Alokasi Dana Desa', True),
            ('PBH', 'Bagi Hasil Pajak', True),
            ('01', 'Penyelengaraan Pemerintahan Desa', False),
            ('02', 'Pelaksanaan Pembangunan Desa', False),
            ('03', 'Pembinaan Kemasyarakatan', False),
            ('04', 'Pemberdayaan Masyarakat', False),
            ('05', 'Bidang Tidak Terduga', False)
        ]

        for budget_type in budget_types:
            bt = BudgetType()
            bt.code = budget_type[0]
            bt.name = budget_type[1]
            bt.is_revenue = budget_type[2]
            result.append(bt)
        return result
