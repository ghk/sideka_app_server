from tatakelola import db
from tatakelola.models import Summary
from tatakelola.helpers import SummaryPendudukTransformer, SummaryApbdesTransformer
from tatakelola.repository import PendudukRepository, RegionRepository, ApbdesRepository

region_repository = RegionRepository(db)
penduduk_repository = PendudukRepository(db)
apbdes_repository = ApbdesRepository(db)


class Generator:
    @staticmethod
    def generate_penduduk_summary_by_region(summary, region):
        penduduks = penduduk_repository.get_by_region(region.id)
        summary = SummaryPendudukTransformer.transform(summary, penduduks)
        summary.fk_region_id = region.id
        return summary

    @staticmethod
    def generate_apbdes_summary_by_region(summary, region):
        apbdes = apbdes_repository.get_by_region(region.id)

        if len(apbdes) == 0:
            return summary

        summary = SummaryApbdesTransformer.transform(summary, apbdes)
        summary.fk_region_id = region.id
        return summary

    @staticmethod
    def generate_summaries():
        result = []
        regions = region_repository.all()
        for region in regions:
            summary = Summary()
            summary = Generator.generate_penduduk_summary_by_region(summary, region)
            summary = Generator.generate_apbdes_summary_by_region(summary, region)
            summary.fk_region_id = region.id
            result.append(summary)
        return result
