from tatakelola import db
from tatakelola.helpers import SummaryTransformer
from tatakelola.repository import PendudukRepository, RegionRepository

region_repository = RegionRepository(db)
penduduk_repository = PendudukRepository(db)

class Generator:
    @staticmethod
    def generate_penduduk_summary_by_region(region):
        penduduks = penduduk_repository.get_by_region(region.id)
        return SummaryTransformer.transform(penduduks, region)

    @staticmethod
    def generate_penduduk_summaries():
        result = []
        regions = region_repository.all()
        for region in regions:
            summary = Generator.generate_penduduk_summary_by_region(region)
            result.append(summary)
        return result
