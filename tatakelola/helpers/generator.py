from tatakelola import db
from tatakelola.models import Summary
from tatakelola.helpers import SummaryPendudukTransformer, SummaryApbdesTransformer, SummaryGeojsonTransformer
from tatakelola.repository import PendudukRepository, RegionRepository, ApbdesRepository, GeojsonRepository, SummaryRepository

region_repository = RegionRepository(db)
penduduk_repository = PendudukRepository(db)
apbdes_repository = ApbdesRepository(db)
summary_repository = SummaryRepository(db)
geojson_repository = GeojsonRepository(db)

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
    def generate_geojson_summary_by_region(summary, region):
        boundaries = geojson_repository.get_by_type_and_region('boundary', region.id)
        landuse = geojson_repository.get_by_type_and_region('landuse', region.id)

        summary.pemetaan_desa_boundary = None
        summary.pemetaan_potential_farmland = 0
        summary.pemetaan_potential_forest = 0
        summary.pemetaan_potential_orchard = 0
        summary.pemetaan_water_spring = 0
        summary.pemetaan_water_river = 0
        summary.pemetaan_water_ditch = 0
        summary.pemetaan_electricity_available_kk = 0

        if boundaries is not None:
            summary = SummaryGeojsonTransformer.transform(summary, boundaries.data, 'boundary', 'admin_level')
        if landuse is not None:
            summary = SummaryGeojsonTransformer.transform(summary, landuse.data, 'landuse', 'landuse')

        return summary

    @staticmethod
    def generate_summaries():
        result = []
        regions = region_repository.all()
        for region in regions:
            summary_repository.delete_by_region(region.id)
            summary = Summary()
            summary = Generator.generate_penduduk_summary_by_region(summary, region)
            summary = Generator.generate_apbdes_summary_by_region(summary, region)
            summary = Generator.generate_geojson_summary_by_region(summary, region)
            summary.fk_region_id = region.id
            result.append(summary)
        return result