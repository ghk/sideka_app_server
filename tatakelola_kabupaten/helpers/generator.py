from tatakelola_kabupaten import db
from tatakelola_kabupaten.models import Summary, Layout, Boundary
from tatakelola_kabupaten.helpers import SummaryPendudukTransformer, SummaryApbdesTransformer, SummaryGeojsonTransformer, LayoutTransformer
from tatakelola_kabupaten.repository import PendudukRepository, RegionRepository, ApbdesRepository, GeojsonRepository, SummaryRepository, LayoutRepository, BoundaryRepository

region_repository = RegionRepository(db)
penduduk_repository = PendudukRepository(db)
apbdes_repository = ApbdesRepository(db)
summary_repository = SummaryRepository(db)
geojson_repository = GeojsonRepository(db)
layout_repository = LayoutRepository(db)
boundary_repository = BoundaryRepository(db)

class Generator:
    @staticmethod
    def generate_summaries(code):
        result = []
        regions = region_repository.get_all_by_kabupaten_code(code)

        for region in regions:
            summary_repository.delete_by_region(region.id)
            summary = Summary()
            summary = Generator.generate_penduduk_summary_by_region(summary, region)
            summary = Generator.generate_apbdes_summary_by_region(summary, region)
            summary = Generator.generate_geojson_summary_by_region(summary, region)
            summary.fk_region_id = region.id
            result.append(summary)
        return result

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
        facilities = geojson_repository.get_by_type_and_region('facilities_infrastructures', region.id)
        transportations = geojson_repository.get_by_type_and_region('network_transportation', region.id)

        summary.pemetaan_landuse_forest = 0
        summary.pemetaan_landuse_farmland = 0
        summary.pemetaan_landuse_orchard = 0
        summary.pemetaan_landuse_forest_area = 0
        summary.pemetaan_landuse_farmland_area = 0
        summary.pemetaan_landuse_orchard_area = 0
        summary.pemetaan_school_tk = 0
        summary.pemetaan_school_sd = 0
        summary.pemetaan_school_smp = 0
        summary.pemetaan_school_sma = 0
        summary.pemetaan_school_pt = 0
        summary.pemetaan_desa_boundary = 0
        summary.pemetaan_dusun_total = 0
        summary.pemetaan_desa_circumference = 0

        summary.pemetaan_highway_asphalt_length = 0
        summary.pemetaan_highway_concrete_length = 0
        summary.pemetaan_highway_other_length = 0
        summary.pemetaan_bridge_length = 0

        if boundaries is not None:
            summary = SummaryGeojsonTransformer.transform(summary, boundaries.data, 'boundary')
        if landuse is not None:
            summary = SummaryGeojsonTransformer.transform(summary, landuse.data, 'landuse')
        if facilities is not None:
            sumamry = SummaryGeojsonTransformer.transform(summary, facilities.data, 'facilities_infrastructures')
        if transportations is not None:
            summary = SummaryGeojsonTransformer.transform(summary, transportations.data, 'network_transportation')
        return summary

    @staticmethod
    def generate_layouts(code):
        result = []
        regions = region_repository.get_all_by_kabupaten_code(code)

        for region in regions:
            penduduks = penduduk_repository.get_by_region(region.id)
            geojsons = geojson_repository.get_by_region(region.id)

            layout_repository.delete_by_region(region.id)
            layout = Layout()
            layout = LayoutTransformer.transform(layout, geojsons, penduduks)
            layout.fk_region_id = region.id
            result.append(layout)

        return result

    @staticmethod
    def generate_boundaries(code):
        regions = region_repository.get_all_by_kabupaten_code(code)
        boundary_repository.delete()
        boundary = Boundary()
        boundary.data = []
        boundary.kabupaten_code = code
        
        for region in regions:
            geojsons = geojson_repository.get_by_region(region.id)
            boundary_data = filter(lambda x:x.type == "boundary", geojsons)
        
            if len(boundary_data) > 0:
                for feature in boundary_data[0].data["features"]:
                    if feature["geometry"]["type"] == "Polygon":
                        feature["properties"]["regionId"] = region.id
                        feature["properties"]["regionName"] = region.name
                        boundary.data.append(feature)

        return boundary